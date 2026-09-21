#!/usr/bin/env python3
"""Monitor upstream domain rules. Only the baseline may be written by the bot."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UPSTREAM = 'https://raw.githubusercontent.com/ddgksf2013/Filter/refs/heads/master/AppleIntelligence.list'
BASELINE = 'upstream/AppleIntelligence.list'
BRANCH = 'automation/apple-ai-upstream'
MARKER = '<!-- apple-ai-upstream-monitor -->'
LIMIT = 65536
KINDS = {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'}


def parse(text):
    if not text or len(text.encode('utf-8')) > LIMIT:
        raise ValueError('Empty or oversized upstream content')
    if re.search(r'<\s*(?:!doctype|html|body|script)\b', text, re.I):
        raise ValueError('HTML received instead of a rule list')
    rules = set()
    for number, line in enumerate(text.lstrip('\ufeff').splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 2 or parts[0].upper() not in KINDS:
            raise ValueError(f'Unsupported rule syntax at line {number}')
        kind, value = parts[0].upper(), parts[1].lower()
        if kind == 'DOMAIN-KEYWORD':
            valid = re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,252}', value)
        else:
            labels = value.split('.')
            valid = (len(value) <= 253 and len(labels) >= 2 and
                     all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', p) for p in labels)
                     and re.fullmatch(r'[a-z]{2,63}|xn--[a-z0-9-]+', labels[-1]))
        if not valid:
            raise ValueError(f'Invalid domain/keyword at line {number}')
        rule = (kind, value)
        if rule in rules:
            raise ValueError(f'Duplicate rule at line {number}')
        rules.add(rule)
    if not 3 <= len(rules) <= 200:
        raise ValueError('Abnormal rule count: expected 3 to 200')
    return rules


def validate_change(old, new):
    if len(new) < len(old) * 0.5 or len(new) > len(old) * 2:
        raise ValueError('Rule count changed by an abnormal amount; manual review required')
    if len(old - new) > len(old) * 0.5:
        raise ValueError('More than half the baseline rules disappeared; manual review required')


def canonical(rules):
    return '\n'.join(f'{k},{v}' for k, v in sorted(rules)) + '\n'


def report(old, new):
    removed, added = old - new, new - old
    rows = [MARKER, '# Apple AI 上游规则变更待测试', '',
            f'来源：{UPSTREAM}', '',
            f'已确认基准 {len(old)} 条 → 最新上游 {len(new)} 条。', '',
            '此 PR 只更新上游基准，不修改两个正式订阅，不判断 GPT / Direct 归属。', '',
            '## 新增规则', '```text', canonical(added).strip() or '无', '```', '',
            '## 删除规则', '```text', canonical(removed).strip() or '无', '```', '',
            '## 匹配方式变化', '']
    shared = sorted({v for _, v in added} & {v for _, v in removed})
    for value in shared:
        before = ', '.join(sorted(k for k, v in removed if v == value))
        after = ', '.join(sorted(k for k, v in added if v == value))
        rows.append(f'- `{value}`：`{before}` → `{after}`')
    if not shared:
        rows.append('无可确定的同域名匹配方式变化。')
    rows += ['', '域名替换按删除旧域名和新增域名列出，不推断两者的一一对应关系。', '',
             '## 人工处理', '', '- [ ] 核查变更并实测相关功能',
             '- [ ] 决定加入 GPT、加入 Direct 或暂不加入',
             '- [ ] 如需调整正式订阅，单独人工修改',
             '- [ ] 确认本批上游已处理后，合并此 PR 更新基准', '',
             '即使决定暂不采用新域名，也可以合并此基准 PR 表示已审阅。',
             '只关闭而不合并不会确认基准，下次检查仍会提醒。',
             '请勿在此自动化分支编辑正式订阅。机器人不会自动合并。']
    return '\n'.join(rows) + '\n'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected HTTP redirect; stopped safely')


OPENER = urllib.request.build_opener(NoRedirect)


def download():
    req = urllib.request.Request(UPSTREAM, headers={'User-Agent': 'Apple-AI-Upstream-Monitor'})
    with OPENER.open(req, timeout=30) as response:
        if response.status != 200 or 'text/plain' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Unexpected upstream response status or content type')
        raw = response.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('Upstream exceeds size limit')
    return raw.decode('utf-8-sig')


class GitHub:
    def __init__(self, repo, token):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('Invalid repository')
        self.root = f'https://api.github.com/repos/{repo}'
        self.token = token

    def api(self, method, path, data=None, missing=False):
        req = urllib.request.Request(self.root + path,
            data=None if data is None else json.dumps(data).encode(), method=method,
            headers={'Authorization': f'Bearer {self.token}', 'Accept': 'application/vnd.github+json',
                     'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Apple-AI-Upstream-Monitor',
                     'Content-Type': 'application/json'})
        try:
            with OPENER.open(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if missing and exc.code == 404:
                return None
            raise RuntimeError(f'GitHub API {method} {path}: HTTP {exc.code}') from None

    def file(self, ref):
        result = self.api('GET', f'/contents/{BASELINE}?ref={urllib.parse.quote(ref, safe="")}')
        return base64.b64decode(result['content']).decode('utf-8')


def sync(gh, repo, base, old, new, text):
    base_ref = urllib.parse.quote(base, safe='')
    main = gh.api('GET', f'/git/ref/heads/{base_ref}')['object']['sha']
    # A manual baseline update during the run must never be silently overwritten.
    if parse(gh.file(main)) != old:
        raise RuntimeError('Confirmed baseline changed during this run; rerun workflow')
    query = urllib.parse.urlencode({'state': 'open', 'head': repo.split('/')[0] + ':' + BRANCH,
                                  'base': base, 'per_page': 100})
    prs = gh.api('GET', '/pulls?' + query)
    if len(prs) > 1 or any(MARKER not in (p.get('body') or '') for p in prs):
        raise RuntimeError('Unexpected PR on reserved automation branch')
    pending = gh.api('GET', '/git/ref/heads/' + BRANCH, missing=True)
    previous = None
    if pending:
        head = pending['object']['sha']
        comparison = gh.api('GET', f'/compare/{main}...{head}')
        if any(f['filename'] != BASELINE for f in comparison.get('files', [])):
            raise RuntimeError('Automation branch contains unrelated edits; stopped safely')
        previous = parse(gh.file(head))
    if previous != new:
        tree = gh.api('GET', '/git/commits/' + main)['tree']['sha']
        tree = gh.api('POST', '/git/trees', {'base_tree': tree, 'tree': [
            {'path': BASELINE, 'mode': '100644', 'type': 'blob', 'content': text}]})['sha']
        # Both parents keep the branch fast-forwardable and include the current main.
        parents = list(dict.fromkeys(([pending['object']['sha']] if pending else []) + [main]))
        commit = gh.api('POST', '/git/commits', {'message': 'chore: review Apple AI upstream changes',
                        'tree': tree, 'parents': parents})['sha']
        if pending:
            gh.api('PATCH', '/git/refs/heads/' + BRANCH, {'sha': commit, 'force': False})
        else:
            gh.api('POST', '/git/refs', {'ref': 'refs/heads/' + BRANCH, 'sha': commit})
    body = report(old, new)
    if not prs:
        pr = gh.api('POST', '/pulls', {'title': 'Apple AI：上游规则变更待测试', 'body': body,
                    'head': BRANCH, 'base': base})
    else:
        pr = prs[0]
        if pr.get('body') != body:
            gh.api('PATCH', f'/pulls/{pr["number"]}', {'body': body})
    # Comment per distinct baseline/candidate pair: repairs partial failures, no weekly spam.
    digest = hashlib.sha256((canonical(old) + '\n' + canonical(new)).encode()).hexdigest()
    marker = f'<!-- apple-ai-notice:{digest} -->'
    found = False
    page = 1
    while True:
        comments = gh.api('GET', f'/issues/{pr["number"]}/comments?per_page=100&page={page}')
        found |= any(marker in c.get('body', '') for c in comments)
        if found or len(comments) < 100:
            break
        page += 1
    if not found:
        gh.api('POST', f'/issues/{pr["number"]}/comments', {'body': marker + '\n上游发现新的规则差异，新增、删除和匹配方式变化已更新到 PR 正文。请实测后人工决定；两个正式订阅未修改。'})
    return pr['html_url']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, help='Local fixture instead of HTTP download')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.candidate and not args.dry_run:
        parser.error('--candidate requires --dry-run')
    old = parse(Path(BASELINE).read_text(encoding='utf-8'))
    text = args.candidate.read_text(encoding='utf-8') if args.candidate else download()
    new = parse(text)
    validate_change(old, new)
    if old == new:
        message = f'No rule changes ({len(new)} rules). No commit, PR or file changes.'
    elif args.dry_run:
        message = report(old, new)
    else:
        repo = os.environ['GITHUB_REPOSITORY']
        gh = GitHub(repo, os.environ['GITHUB_TOKEN'])
        message = 'Pending review: ' + sync(gh, repo, os.environ['BASE_BRANCH'], old, new, text)
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(message + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'::error::{error}', file=sys.stderr)
        sys.exit(1)
