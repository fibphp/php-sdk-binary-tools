# -*- coding: utf-8 -*-
import re
import os
import sys
import json


def read_lines(f):
    with open(f, 'r') as rf:
        return rf.readlines()


def dump_json(f, obj):
    with open(f, 'w') as wf:
        json.dump(obj, wf, indent=2)


def load_json(f):
    with open(f, 'r') as rf:
        return json.load(rf)


def _LOG(msg, handle=None):
    print msg
    if handle:
        handle.write(msg + '\n')
        handle.flush()


# ===============================================================
# ========================== LETX ERROR ==========================
# ===============================================================

class Error(Exception):
    pass


class NotMatchError(Error):
    def __init__(self, index, msg, obj=None):
        super(NotMatchError, self).__init__(msg)
        self._letx = obj
        self.index = index

    def __str__(self):
        return '%s' % (self.message,)


class ListNotMatchError(NotMatchError):
    def __init__(self, index, msg, tag_list, ex_list, obj=None):
        super(ListNotMatchError, self).__init__(index, msg, obj)
        self.__dict__.update(dict(zip(tag_list, ex_list)))
        self.index = index
        max_item = max(ex_list, key=lambda i: i.index)
        self._ex = {tag_list[i]: item for (i, item) in enumerate(ex_list) if item.index == max_item.index}

    def __str__(self):
        return '%s >>>>\n %s' % (
            self.message, '\n'.join(['\t<%s> :%s' % (key, item) for (key, item) in self._ex.items()]))


# ===============================================================
# ========================== LETX MAIN ==========================
# ===============================================================

class _log(object):
    debug = False

    def log(self, msg, handle=None):
        if self.debug and msg:
            _msg = msg.replace("\n", r"\n")
            print _msg
            if handle:
                handle.write(_msg + '\n')
                handle.flush()


class _base(_log):
    TestFalse = object()

    def test(self, index, s, sl):
        try:
            index, val = self.__call__(index, s, sl)
            return index, val
        except NotMatchError as ex:
            _ = '%s test NotMatchError:%r @%d<`...%s...`>' % (self, ex, index, SUB(s, index))
            return index, self.TestFalse

    def __call__(self, index, s, sl):
        assert index < sl, 'base index:%s out of max_len:%s.' % (index, sl)
        return None, index

    def __repr__(self):
        return '<%s at 0x%08x>' % (str(self), id(self))

    def __str__(self):
        return 'callable letx %s:%s' % (
            str(self.__class__).split("'")[1].replace('__main__.', ''), getattr(self, '__tag__', 'unknown'))


BY_ORDER = 1
MAX_INDEX = 2


class LetxBuild(_log):
    def __init__(self, _sdic, mtag='_'):
        assert isinstance(_sdic, dict) and '<_>' in _sdic and isinstance(_sdic['<_>'], list), \
            'input:%s must as {"<_>": [...]}.' % (_sdic,)

        PKG_MAP = build_pkg_map()

        def pre_pkg(tag, pkg_tag, pkg_dict):
            pkg_tag = pkg_tag.strip()
            if pkg_tag in PKG_MAP:
                return PKG_MAP[pkg_tag](tag)
            if pkg_tag in pkg_dict:
                return pkg_dict[pkg_tag]
            if tag in pkg_dict:
                return pkg_dict[tag]
            return DEFAULT_PKG

        def pre_env(s, pkg_dict, fix=''):
            def setkey(_env, key, val=None):
                assert key not in _env, 'mutil tag in key:%s' % (key,)
                _env[key] = val

            env = {}
            if isinstance(s, dict) and len(s) == 1:
                k, v = s.items()[0]
                arr = k.split('#', 1)
                k = arr[0]
                if IS_TAG(k):
                    pkg_tag = arr[1] if len(arr) == 2 else ''
                    tag = k[1:-1]
                    pkg = pre_pkg(tag, pkg_tag, pkg_dict)
                    setkey(env, '#' + tag, pkg)
                    v = [v, ] if not isinstance(v, list) else v
                    setkey(env, tag)
                    for i, item in enumerate(v):
                        env.update(pre_env(item, pkg_dict, '%s#%s' % (k[1:-1], i)))

                    return env

            setkey(env, fix)
            return env

        _tag_dict = {'<_>': _sdic['<_>']}
        _func_dict = {k: v for k, v in _sdic.items() if IS_FUN(k)}
        _pkg_dict = {k[1:]: v for k, v in _sdic.items() if k.startswith('#')}

        self.mtag = mtag
        self._stack = []
        self._env = pre_env(_tag_dict, _pkg_dict)
        self._parse = self.comp_letx(_tag_dict, _func_dict)
        self.base_list_mode = BY_ORDER
        assert hasattr(self._parse, '__call__'), 'comp_letx self._parse must callable.'

    def parse(self, str_in):
        index, ret = self._parse(0, str_in, len(str_in))
        return index, ret

    def find_tag(self, tag_in):
        if not tag_in:
            def _null_parse(index_in, str_in, str_len):
                index = SKIP_SPACE(index_in, str_in, str_len)
                return index, ''

            return _null_parse

        tag_in = tag_in[1:] if tag_in[0] == '!' else tag_in
        assert tag_in in self._env, 'comp_letx find_tag:can not find(%s) in %s.' % (tag_in, self._env)

        def _pkg_parse(index_in, str_in, str_len):
            assert self._env[tag_in], 'comp_letx _pkg_parse:empty value (%s) in %s.' % (tag_in, self._env)
            _parse_func, _pkg, _ = self._env[tag_in]
            index, ret_tmp = _parse_func(index_in, str_in, str_len)
            ret = _pkg(ret_tmp)
            return index, ret

        _pkg_parse.func_name = 'letx %s' % (tag_in,)
        return _pkg_parse

    def comp_letx(self, tag_dict, func_dict):
        def add_tag(nk, env, val):
            assert nk in env and env[nk] is None, 'comp_letx add_tag:mutil tag %s in %s.' % (nk, env)
            env[nk] = val

        def comp_tag(args, _func_dict, _fix_tag):
            if hasattr(args, '__call__'):
                return _fix_tag, args
            elif isinstance(args, (str, unicode, tuple)):
                return comp_tag({'><': args}, _func_dict, _fix_tag)
            elif isinstance(args, dict):
                assert len(args) == 1, 'comp_tag tag|func dict item:%s must len==1.' % (args,)
                _k, _v = args.items()[0]
                _k = _k.split('#', 1)[0]
                if IS_FUN(_k):
                    assert _k in _func_dict, 'comp_tag func dict item:%s must in fdic:%s.' % (_k, _func_dict)
                    return _fix_tag, _func_dict[_k](_v, self)
                elif IS_TAG(_k):
                    tmp_func = self.comp_letx(args, _func_dict)
                    return _k[1:-1], tmp_func
            else:
                assert False, 'comp_tag item:%s not support.' % (args,)

        assert isinstance(tag_dict, dict) and len(tag_dict) == 1, 'comp_letx item:%s must dict and len==1.' % (
            tag_dict,)
        k, v = tag_dict.items()[0]
        k = k.split('#', 1)[0]
        assert IS_TAG(k) and '#' not in k, 'comp_letx tag dict item:%s must tag(`#` not in it).' % (k,)
        _main_tag = k[1:-1]
        pkg = self._env.get('#' + _main_tag, DEFAULT_PKG)
        assert hasattr(pkg, '__call__'), 'pkg for tag %s must callable.' % (_main_tag,)

        letx_list = [v, ] if not isinstance(v, list) else v
        parse_func, tag_list = None, []
        for i, item in enumerate(letx_list):
            fix_tag = '%s#%s' % (_main_tag, i)
            tag, parse_func = comp_tag(item, func_dict, fix_tag)
            if tag == fix_tag:
                add_tag(tag, self._env, (parse_func, DEFAULT_PKG, item))
            tag_list.append(tag)

        func_obj = base_list((_main_tag, tag_list), self) if len(letx_list) > 1 else parse_func
        add_tag(_main_tag, self._env, (func_obj, pkg, letx_list))
        return self.find_tag(self.mtag) if _main_tag == '_' else self.find_tag(_main_tag)


# ===============================================================
# ========================== HELP FUNC ==========================
# ===============================================================

IS_TAG = lambda k, sa='<', sb='>': len(k) >= 2 and k[0] == sa and k[-1] == sb
IS_FUN = lambda k, sa='>', sb='<': len(k) >= 2 and k[0] == sa and k[-1] == sb
IS_REGEXP = lambda k, sa='</', sb='/>': len(k) >= 4 and k[:2] == sa and k[-2:] == sb
IS_REAL = lambda k, sa='<`', sb='`>': len(k) >= 4 and k[:2] == sa and k[-2:] == sb

DEFAULT_SPACE = {'\n': 1, '\r': 1, '\t': 1, ' ': 1}

SUB = lambda s, index, n=5: s[index - n:index + n]


def build_pkg_map(MAX_N=9, F_MAP=(('', lambda x: x), ('^int', int), ('^long', long), ('^float', float))):
    base_map = {
        '': lambda x: x,
        'N': lambda x: None,
        'T': lambda x: True,
        'F': lambda x: False,
        '{:}': lambda x: {k: v for k, v in x},
    }
    tpl_map = {
        '{$t:}': lambda tag, idx, f: lambda x: {tag: x},
        '$i~': lambda tag, idx, f: lambda x: x[idx:],
        '~$i': lambda tag, idx, f: lambda x: x[:idx],
        '$i^f': lambda tag, idx, f: lambda x: f(x[idx]),
        '[$i~]': lambda tag, idx, f: lambda x: [i[idx:] for i in x],
        '[~$i]': lambda tag, idx, f: lambda x: [i[:idx] for i in x],
        '[$i^f]': lambda tag, idx, f: lambda x: [f(i[idx]) for i in x],
        '{$t:$i~}': lambda tag, idx, f: lambda x: {tag: x[idx:]},
        '{$t:~$i}': lambda tag, idx, f: lambda x: {tag: x[:idx]},
        '{$t:$i^f}': lambda tag, idx, f: lambda x: {tag: f(x[idx])},
        '{$t:[$i~]}': lambda tag, idx, f: lambda x: {tag: [i[idx:] for i in x]},
        '{$t:[~$i]}': lambda tag, idx, f: lambda x: {tag: [i[:idx] for i in x]},
        '{$t:[$i^f]}': lambda tag, idx, f: lambda x: {tag: [f(i[idx]) for i in x]},
    }
    ext_map = {}
    for expr, func in tpl_map.items():
        if '$i' in expr:
            for n in range(0, MAX_N):
                _expr = expr.replace('$i', str(n))
                tmp_map = {_expr.replace('^f', v): vf for v, vf in F_MAP} if '^f' in _expr else {
                    _expr: lambda x: x}
                for e, vf in tmp_map.items():
                    ext_map[e] = lambda tag, idx=n, f=vf, _func=func: _func(tag, idx, f)
        else:
            ext_map[expr] = lambda tag, idx=None, f=None, _func=func: _func(tag, idx, f)

    for expr, func in base_map.items():
        ext_map[expr] = lambda tag, _func=func: _func
    return ext_map


def DEFAULT_PKG(x):
    return x


def SKIP_SPACE(si, ss, sslen, B=None):
    if B is None:
        B = DEFAULT_SPACE
    while si < sslen and ss[si] in B:
        si += 1
    return si


def _SPLIT_REG(s, sa='<', sb='>'):
    assert isinstance(s, basestring) and s, '_SPLIT_REG:`%s` is not basestring.' % (s,)
    ret, ib, ia = [], 0, s.find(sa)
    while ia >= 0:
        if ia > ib:
            ret.append(s[ib:ia])
        _ia, ib = ia, s.find(sb, ia) + 1
        ia = s.find(sa, ia + 1)
        assert ia < 0 or ia >= ib > _ia, '_SPLIT_REG:`%s` <> not match.' % (s,)
        ret.append(s[_ia:ib])
        if ia < 0 and s[ib:]:
            assert s.find(sb, ib) < 0, '_SPLIT_REG:`%s` <> not match at end.' % (s,)
            ret.append(s[ib:])

    if not ret:
        ret.append(s)

    return tuple([i.strip() for i in ret if i.strip()])


def GBK(s):
    try:
        return s.decode('utf-8').encode('gbk')
    except UnicodeDecodeError:
        return repr(s)


# ===============================================================
# ========================= MATCH FUNC ==========================
# ===============================================================

def fstr(QUOTES, ESCAPE='\\'):  ##i[si] is " or ', return index of next i[si] without \ before it
    QUOTES = QUOTES.strip()

    def _fstr(index, s, sl):
        if s[index] != QUOTES:
            msg = 'fstr not start s[%s:]<`...%s...`>,`%s`.' % (index, s[index], QUOTES)
            raise NotMatchError(index, msg, _fstr)
        _index = index + 1
        while _index < sl and s[_index] != QUOTES:
            _index += 2 if s[_index] == ESCAPE else 1
        if s[_index] != QUOTES:
            msg = 'fstr not end s[%s:]<`...%s...`>,`%s`.' % (index, s[index], QUOTES)
            raise NotMatchError(_index, msg, _fstr)
        return _index + 1, s[index + 1:_index]

    return _fstr


def ftoken(END, PRE=None, SKIP=None):
    def _ftoken(index, s, sl):
        while PRE and index < sl and s[index] in PRE:
            index += 1

        if index >= sl:
            msg = 'out of str length %d at %d' % (sl, index)
            raise NotMatchError(index, msg, _ftoken)

        if s[index] in END:
            msg = 'ftoken not start s[%s:]<`...%s...`>,`%s`.' % (index, SUB(s, index), s[index])
            raise NotMatchError(index, msg, _ftoken)
        val = []
        while index < sl and s[index] not in END:
            if SKIP and s[index] in SKIP:
                pass
            else:
                val.append(s[index])
            index += 1
        return index, ''.join(val)

    return _ftoken


class base_list(_base):
    def __init__(self, args_tuple, letx):
        main_tag, tag_list = args_tuple
        assert main_tag and isinstance(tag_list, (tuple, list)), \
            'base_list `%s` and `%s` must tuple or list.' % (main_tag, tag_list)

        self.func_list = [letx.find_tag(tag) for tag in tag_list]
        self.__tag__ = '<%s>`%s`' % (main_tag, ','.join(tag_list))
        self.main_tag, self.tag_list = main_tag, tag_list
        self.letx = letx

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        if getattr(self.letx, 'base_list_mode', BY_ORDER) == MAX_INDEX:
            ex_list = []
            ret_list = []
            for _, func in enumerate(self.func_list):
                try:
                    idx, ret = func(index, s, sl)
                    ret_list.append((idx, ret))
                except NotMatchError as ex:
                    ex_list.append(ex)

            max_idx = max([i for i, _ in ret_list]) if ret_list else 0
            for idx, ret in ret_list:
                if max_idx == idx:
                    return idx, ret

            msg = '%s cannot match @%s<`...%s...`>.' % (str(self), index, SUB(s, index))
            raise ListNotMatchError(index, msg, self.tag_list, ex_list, self)
        else:
            ex_list = []
            for _, func in enumerate(self.func_list):
                try:
                    index, ret = func(index, s, sl)
                    return index, ret
                except NotMatchError as ex:
                    ex_list.append(ex)

            msg = '%s cannot match @%s<`...%s...`>.' % (str(self), index, SUB(s, index))
            raise ListNotMatchError(index, msg, self.tag_list, ex_list, self)


class base_reg(_base):
    def __init__(self, args_tuple_or_str, letx):
        args_tuple = _SPLIT_REG(args_tuple_or_str) if isinstance(args_tuple_or_str, basestring) else \
            args_tuple_or_str
        assert args_tuple and isinstance(args_tuple, tuple), 'base_reg `%s` must tuple.' % (args_tuple,)
        for idx, item in enumerate(args_tuple):
            assert isinstance(item, (str, unicode)), 'base_reg idx %d:`%s` must str or unicode.' % (idx, item)

        tag_split = lambda i: [tag for tag in i[1:-1].split('|')]
        real_split = lambda i: [tag for tag in i[2:-2].split('|') if tag]
        list_split = lambda i: base_list((i[1:-1], tag_split(i)), letx)

        tag_func = lambda i: \
            (re.compile(i[2:-2]), i[2:-2]) if IS_REGEXP(i) else \
                (real_split(i),) if IS_REAL(i) else \
                    (list_split(i), i[1:-1], i[1:-1][0] == '!') if IS_TAG(i) and '|' in i else \
                        (letx.find_tag(i[1:-1]), i[1:-1], i[1:-1] and i[1:-1][0] == '!') if IS_TAG(i) else (i,)

        self.__tag__ = ''.join(args_tuple)
        self.func_list = [tag_func(item) for item in args_tuple if item]
        self.args_tuple = args_tuple
        self.letx = letx

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        ret = []
        for ix, item in enumerate(self.func_list):
            if len(item) == 3 and item[2]:
                pass
            else:
                index = SKIP_SPACE(index, s, sl)

            if index >= sl:
                break

            f_len = len(item)
            if f_len == 1:  ## 匹配字符串
                if isinstance(item[0], (str, unicode)):  # 原始字符串
                    len_i, tmp_i = len(item[0]), item[0]
                    tmp_str = s[index:index + len_i]
                    if not tmp_str == tmp_i:
                        msg = 'base_reg str %s not math @[%s:%s]<`...%s...`>.' % (tmp_i, index, index + len_i, tmp_str)
                        raise NotMatchError(index, msg, self)
                    else:
                        index += len_i
                        msg = 'base_reg str `%s@%d` >>>%s<<< match @%s<`...%s...`>.' % (
                            GBK(str(self)), ix, GBK(tmp_str), index, GBK(SUB(s, index)))
                        self.log(msg)
                else:  # 捕获字符串
                    tmp_i, len_i, tmp_str = '', 0, ''
                    for tmp_i in item[0]:
                        len_i = len(tmp_i)
                        tmp_str = s[index:index + len_i]
                        if not tmp_str == tmp_i:
                            continue
                        else:
                            index += len_i
                            ret.append(tmp_str)
                            msg = 'base_reg str `%s@%d` >>>%s<<< match @%s<`...%s...`>.' % (
                                GBK(str(self)), ix, GBK(tmp_str), index, GBK(SUB(s, index)))
                            self.log(msg)
                            break
                    else:
                        msg = 'base_reg str %s not math @[%s:%s]<`...%s...`>.' % (tmp_i, index, index + len_i, tmp_str)
                        raise NotMatchError(index, msg, self)

            elif f_len == 2:
                reg_tmp, reg_i = item[0].match(s[index:]), item[1]
                tmp = reg_tmp.group() if reg_tmp else None
                if not tmp:
                    msg = 'base_reg reg_exp %s not math @%s<`...%s...`>.' % (reg_i, index, GBK(SUB(s, index)))
                    raise NotMatchError(index, msg, self)
                else:
                    index += len(tmp)
                    ret.append(tmp)
                    msg = 'base_reg reg_exp `%s@%d` >>>%s<<< match @%s<`...%s...`>.' % (
                        GBK(str(self)), ix, tmp, index, GBK(SUB(s, index)))
                    self.log(msg)
            elif f_len == 3:
                index, tmp = item[0](index, s, sl)
                ret.append(tmp)
                msg = 'base_reg tag `%s@%d` >>>%s<<< match @%s<`...%s...`>.' % (
                    GBK(str(self)), ix, tmp, index, GBK(SUB(s, index)))
                self.log(msg)
        return index, tuple(ret)


class base_join(_base):
    def __init__(self, args_tuple, letx):
        assert isinstance(args_tuple, tuple) and len(args_tuple) == 4, \
            'base_join %s must tuple(start, match, split, end).' % (args_tuple,)

        self.func_tuple = [base_reg(item, letx) for item in args_tuple]
        self.__tag__ = '%s%s%s...%s' % args_tuple
        self.letx = letx

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        start, match, split, end = self.func_tuple
        T = lambda x: x is self.TestFalse
        b2s = lambda t: '>>>%s<<<' % (t,) if not T(t) else 'not'

        def get_msg(tag, item, t):
            _msg = 'base_join %s `%s` %s match @%s<`...%s...`>.' % (tag, str(item), b2s(t), index, SUB(s, index))
            self.log(_msg)
            return _msg

        ret = []
        index, is_start = start.test(index, s, sl)
        msg = get_msg('start', start, is_start)
        if T(is_start):
            raise NotMatchError(index, msg, self)

        index, is_end = end.test(index, s, sl)
        while T(is_end):
            self.letx.base_list_mode = MAX_INDEX
            index, tmp = match(index, s, sl)
            self.letx.base_list_mode = BY_ORDER
            get_msg('match', match, tmp)

            ret.append(tmp)
            index, is_split = split.test(index, s, sl)
            get_msg('split', split, is_split)
            index, is_end = end.test(index, s, sl)
            msg = get_msg('end', end, is_end)
            if not T(is_end):
                break
            if T(is_split):
                raise NotMatchError(index, msg, self)

        return index, tuple(ret)


class base_lines(_base):
    def __init__(self, args_tuple, letx):
        assert isinstance(args_tuple, tuple) and (len(args_tuple) == 2 or len(args_tuple) == 3), \
            'base_lines %s must tuple(start, match, [SPLIT_LINE]).' % (args_tuple,)

        self.SPLIT_LINE = args_tuple[2] if len(args_tuple) == 3 else True

        args_tuple = args_tuple[:2]
        self.func_tuple = [base_reg(item, letx) for item in args_tuple]
        self.__tag__ = '%s -> %s' % args_tuple
        self.letx = letx

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        start, match = self.func_tuple
        F = lambda x: x is self.TestFalse
        b2s = lambda t: '>>>%s<<<' % (t,) if not F(t) else 'not'

        def get_msg(tag, item, t):
            _msg = 'base_lines %s `%s` %s math @%s<`...%s...`>.' % (
                tag, GBK(str(item)), b2s(t), index, GBK(SUB(s, index)))
            self.log(_msg)
            return _msg

        ret = []
        index, is_start = start.test(index, s, sl)
        msg = get_msg('start', start, is_start)
        if F(is_start):
            raise NotMatchError(index, msg, self)

        if self.SPLIT_LINE:
            index = SKIP_SPACE(index, s, sl)

        while index < sl:
            try:
                index, tmp = match(index, s, sl)
            except NotMatchError:
                break

            get_msg('match', match, tmp)
            if not tmp:
                break

            if index < sl and s[index] == '\n':
                index += 1

            ret.append(tmp)

        return index, tuple(ret)


# ===============================================================
# ========================== TEST FUNC ==========================
# ===============================================================

def all_test(test_pre='_test'):
    globals_dict = globals()
    for k, v in globals_dict.items():
        if k.startswith(test_pre):
            _LOG("\n\n>>%s" % (k,))
            if hasattr(v, '__call__'):
                v()


def _unittest(func, *cases):
    return [_functest(func, *case) for case in cases]


def _functest(func, isPass, *args, **kws):
    result = None
    try:
        _LOG('\n%s -> %s' % (isPass, func.func_name))
        result = func(*args, **kws)
        _LOG('=%s' % (json.dumps(result, indent=2),))
    except Error as ex:
        _LOG("%s -> %s:%s" % (isPass, type(ex), ex))
        if isPass:
            raise ex
    else:
        if not isPass:
            raise AssertionError("isPass:%s but no Exception!!!" % (isPass,))
    return result


# ===============================================================
# ========================== clbuild HELP ==========================
# ===============================================================

def parse_cl(cmds):
    rets = []
    lines = set()
    for line in cmds.split("\n"):
        line = line.strip()
        if not line or not line.startswith('"cl.exe"') or line in lines:
            continue

        ret = clload(line)
        cl = fix_cl(ret)
        rets.append(cl)
        lines.add(line)

    return rets


def fix_cl(ret, LIST_KEYS=None, MAP_KEYS=None):
    if MAP_KEYS is None:
        MAP_KEYS = {'define': lambda df: df if len(df) == 2 else (df[0], None), 'file': lambda df: df,
                    'warn': lambda df: (df[1], df[0])}
    if LIST_KEYS is None:
        LIST_KEYS = ['include', 'zc', 'flag']
    assert len(ret) == 3 and ret[0] == 'cl.exe', "ret len error"
    assert isinstance(ret[1], dict) and len(ret[1]) == 1 and 'option' in ret[1], "ret option error"
    assert isinstance(ret[2], dict) and len(ret[2]) == 1 and 'input' in ret[2], "ret input error"

    obj = {'cmd': ret[0]}
    obj.update(ret[2])
    for op in ret[1]['option']:
        if not isinstance(op, dict):
            continue

        for mk, mf in MAP_KEYS.items():
            if mk in op:
                k, v = mf(op[mk])
                obj.setdefault(mk, {})
                obj[mk][k] = v
                break
        else:
            for lk in LIST_KEYS:
                if lk in op:
                    obj.setdefault(lk, [])
                    obj[lk].append(op[lk])
                    break

    return obj


# ===============================================================
# ========================== clbuild FUNC ==========================
# ===============================================================

def clbuild():
    with open('nmake_cl.txt', 'r') as rf:
        t0 = rf.read()

    t0 = t0.decode('gbk').encode('utf-8')
    data = parse_cl(t0)
    dump_json('nmake_cl.json', data)
    build_preprocess()
    build_clbuild()
    build_cllink(t0)


def build_cllink(cmds):
    rets = []
    for line in cmds.split("\n"):
        line = line.strip()
        if not line:
            continue

        if not line.startswith('"cl.exe"'):
            rets.append(line + "\n")

    with open(r'cllink.bat', 'w') as wf:
        wf.writelines(rets)


def build_preprocess():
    data = load_json('nmake_cl.json')
    cmds = [
        "@echo off\n"
    ]
    for item in data:
        define = ' '.join(['/D %s' % (k,) if v is None else '/D %s=%s' % (k, v) for k, v in item['define'].items()])
        include = ' '.join(['/I "%s"' % (i,) for i in item['include']])
        zc = ' '.join(['/Zc:%s' % (i,) for i in item['zc']])
        flag = ' '.join(['/%s' % (i,) for i in item['flag']]) + " /P "
        for infile in item['input']:
            outfile = '/Fi:%s' % (infile + "i")
            cmd = r'cl.exe %s %s %s %s %s %s' % (define, include, zc, flag, outfile, infile)
            print cmd
            cmds.append(cmd + "\n")

    with open(r'preprocess.bat', 'w') as wf:
        wf.writelines(cmds)


def build_clbuild():
    data = load_json('nmake_cl.json')
    cmds = [
        "@echo off\n"
    ]
    for item in data:
        define = ' '.join(['/D %s' % (k,) if v is None else '/D %s=%s' % (k, v) for k, v in item['define'].items()])
        include = ' '.join(['/I "%s"' % (i,) for i in item['include']])
        zc = ' '.join(['/Zc:%s' % (i,) for i in item['zc']])
        flag = ' '.join(['/%s' % (i,) for i in item['flag']]) + " /TC /FAs"
        item['file']['a'] = item['file']['o']
        file_f = ' '.join(['/F%s%s' % (k, v) for k, v in item['file'].items()])
        warn = ' '.join(['/w%s%s' % (v, k) for k, v in item[
            'warn'].items()]) + " /wd4090 /wd4047 /wd4146 /wd4244 /wd4267 /wd4216 /wd4018 /wd4113 /wd4101 "

        cmd = r'cl.exe %s %s %s %s %s %s %s' % (
            define, include, zc, file_f, warn, flag, ' '.join([infile + 'ipp' for infile in item['input']]))
        print cmd
        cmds.append(cmd + "\n")

    with open(r'clbuild.bat', 'w') as wf:
        wf.writelines(cmds)


def clean_pp():
    data = load_json('nmake_cl.json')
    base = os.getcwd()
    for item in data:
        for infile in item['input']:
            f = os.path.join(base, infile + 'i')
            outf = f + 'pp'
            do_clean_pp(f, outf)


def do_clean_pp(f, outf):
    lines = read_lines(f)

    ret = []
    include = []
    skip = False
    for line in lines:
        l = line.strip()
        if not l:  # or l.startswith('#pragma') or l.startswith('__pragma'):
            continue

        if l.startswith('#line'):
            # print "\n", l
            aa = l.split(" ", 2)
            ff = aa[2][1:-1] if len(aa) == 3 and len(aa[2]) > 2 and aa[2][0] == '"' and aa[2][-1] == '"' else ""
            if ff.lower().startswith(r'c:\\program files (x86)\\'):
                if not skip:
                    ff = ff.split("\\")[-1]
                    if ff not in include:
                        include.append(ff)
                skip = True
            else:
                skip = False
            continue

        if skip:
            # print 'x',
            pass
        else:
            # print '.',
            ret.append(l + "\n")

    with open(outf, 'w') as wf:
        wf.write("/* auto gen by ipp */\n")
        wf.write("\n")
        for i in include:
            wf.write("#include <%s>\n" % (i,))

        wf.write("\n")
        wf.writelines(ret)

    print "done:", outf, include


# ===============================================================
# ========================== CL LETX  ==========================
# ===============================================================

sdic_cl = {
    '<_>': [
        {'<exe>#0': "<str|token_p>"},
        {'<define>#{$t:1~}': ["<`/|-`>D<token_k>=<token_k>", "<`/|-`>D<token_k>"]},
        {'<include>#{$t:1}': "<`/|-`>I<str|token_p>"},
        {'<file>#{$t:1~}': "<`/|-`>F</[admpRAeori]{1}/><str|token_p>"},
        {'<zc>#{$t:1}': "<`/|-`>Zc:<str|token_k>"},
        {'<warn>#{$t:1~}': "<`/|-`>w</[deo1-4]{1}/><str|token_k>"},
        {'<flag>#{$t:1}': "<`/|-`><str|token_k>"},
        {'<arg>#0': "<define|include|file|zc|warn|flag>"},
        {'<str>': [fstr('"'), fstr("'")]},
        {'<token_k>#0': r"</[\w]+/>"},
        {'<token_p>#0': r"</[:.\/\w\\-]+/>"},
        {'<option>#{$t:[0]}': {'>s_lines<': ("<>", "<arg>")}},
        {'<input>#{$t:[0]}': {'>s_lines<': ("<>", "<str|token_p>")}},
        {'<cl>': "<exe><option><input>"}
    ],
    '><': base_reg,
    '>s_lines<': base_lines, }

clload = lambda s: LetxBuild(sdic_cl, 'cl').parse(s)[1]


def _test_clload():
    t0 = r'''
	type ext\pcre\php_pcre.def > D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php7.dll.def
	"cl.exe" /I "D:\php_sdk\phpdev\vc15\x64\deps\include" /DHAVE_OPENSSL_SSL_H=1 /D COMPILE_DL_OPENSSL /D OPENSSL_EXPORTS=1 /nologo /I . /I main /I Zend /I TSRM /I ext /D _WINDOWS /D WINDOWS=1 /D ZEND_WIN32=1 /D PHP_WIN32=1 /D WIN32 /D _MBCS /W3 /D _USE_MATH_DEFINES /FD /wd4996 /Zc:inline /Zc:__cplusplus /d2FuncCache1 /Zc:wchar_t /MP /LD /MD /W3 /Ox /D NDebug /D NDEBUG /D ZEND_WIN32_FORCE_INLINE /GF /D ZEND_DEBUG=0 /I "D:\php_sdk\phpdev\vc15\x64\deps\include" /D FD_SETSIZE=256 /FoD:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\ext\openssl\ /FpD:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\ext\openssl\ /FRD:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\ext\openssl\ /FdD:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\ext\openssl\ /c ext\openssl\openssl.c ext\openssl\xp_ssl.c
	rc /nologo  /I . /I main /I Zend /I TSRM /I ext /n /fo D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe.res /d WANT_LOGO  /d FILE_DESCRIPTION="\"CLI\"" /d FILE_NAME="\"php.exe\"" /d URL="\"http://www.php.net\"" /d INTERNAL_NAME="\"CLI SAPI\"" /d THANKS_GUYS="\"Thanks to Edin Kadribasic, Marcus Boerger, Johannes Schlueter, Moriyoshi Koizumi, Xinchen Hui\"" win32\build\template.rc
	copy D:\php_sdk\phpdev\vc15\x64\php-src\win32\build\default.manifest D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe.manifest >nul
	"link.exe" /nologo  @"D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\resp\CLI_GLOBAL_OBJS.txt" D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php7.lib ws2_32.lib shell32.lib edit_a.lib D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe.res /out:D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe /nologo /libpath:"D:\php_sdk\phpdev\vc15\x64\deps\lib" /stack:67108864 /libpath:"..\deps\lib"
	if exist D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe.manifest "D:\Windows Kits\10\bin\10.0.19041.0\x64\mt.exe" -nologo -manifest D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe.manifest -outputresource:D:\php_sdk\phpdev\vc15\x64\php-src\x64\Release\php.exe;1
	echo SAPI sapi\cli build complete

'''
    _unittest(parse_cl, (True, t0))


sdic_json = {
    '<_>': [
        {'<str>': [fstr('"'), fstr("'")]},
        {'<None>#N': "None"},
        {'<True>#T': "True"},
        {'<False>#F': "False"},
        {'<num>#0^int': r"</\d+/>"},
        {'<list>#[0]': {'>join<': ("[", "<_>", ",", "]")}},
        {'<list2>#[0]': {'>join<': ("[", "<_>", ",,", "]")}},
        {'<dict>#{:}': {'>join<': ("{", "<str|num|token>:<_>", ",", "}")}},
        {'<token>': ftoken(END={'{', '}', '[', ']', ':', ','}, SKIP={' ', '\r', '\n', '\t'})}
    ],
    '><': base_reg,
    '>join<': base_join, }

load = lambda s: LetxBuild(sdic_json).parse(s)[1]


# ===========TEST==========

def _test1():
    t0 = "[34,,56]"
    t1 = "{'test':123, [1,2,3]:'error here.'}"
    t2 = "[45,]"
    t3 = "['fgh',7656,None,True,False,123,7472,98,[],{},]"
    _unittest(load, (True, t0), (False, t1), (True, t2), (True, t3))


def _test2():
    t0 = "{76:554}"
    t1 = "{'a':4,'a':[],}"
    t2 = "{}"
    t3 = "{'fg':556,}"
    _unittest(load, (True, t0), (True, t1), (True, t2), (True, t3))


def _test3():
    t0 = "[34,4,]"
    t1 = "[ture,]"
    t2 = "    [4.   5,    [    ],   {'a'   : 'b',    }   ]"
    t3 = "   ['fgh',7656,None,  True,False  ,123,   7472,[]  ,{},]  "
    _unittest(load, (True, t2))
    # _unittest(load, (True, t0), (True, t1), (True, t2), (True, t3))


# ===============================================================
# ========================== ASM LETX  ==========================
# ===============================================================

def line_str(PRE, ENDLINE=('\n', '\r')):  ##i[si] is PRE, return index of endline
    PRE = PRE.strip()

    def _lstr(index, s, sl):
        if s[index] != PRE:
            msg = 'lstr not start s[%s:]<`...%s...`>,`%s`.' % (index, s[index], PRE)
            raise NotMatchError(index, msg, _lstr)

        _index = index + 1
        while _index < sl:
            _index += 1
            if s[_index] in ENDLINE:
                return _index + 1, s[index + 1:_index]

        return sl, s[index + 1:sl]

    return _lstr


README = u"""
语法描述为
{<tag>:([tag_item1, tag_item2,...], lambda x:...)} 依次尝试 tag_item,然后 pkg 结果，tag_item 只有一个时，可简写 {<tag>:(tag_item, pkg)}
example
{
    <_>: ##  main_tag 为 <_>, tag中不允许有`#`
        ( [{<tag1>: ([tag_item1, tag_item2,...], lambda x:...)}, ## 可以定义 tag 每一个 tag 都为 letx.find_tag('<tag>') 可获取此 tag 的解析函数
           {<tag2>: ({>func<: agrs}, lambda x:...)}, ## 表示调用函数`func`获取结果
           {<tag3>: (agrs, lambda x:...)}, ## func 为 base_func 时可以直接写参数 等同于{<tag3>: ({><: agrs}, lambda x:...)}
           {>func<: agrs}, ## tag可以匿名(补全为tag#index)，等同于{<tag#index>: ({>func<:agrs}, lambda x:x)}
           (agrs), ## 等同于 {<tag#index>: ({><: agrs}, lambda x:x)}
           callable_obj, ## callable_obj 参数为(_index当前索引, s原字符串, sl原字符串长度)的可调用对象，匹配则返回结果为 (index下一个带解析处索引,ret获取到的结果)，不匹配raise NotMatchError
            ],
          pkg lambda x:...`) ## 处理tag返回结果的函数
    ><:base_func, ##  base_func 为 ><
    >func<:func, ## func 接受两个参数 (args, letx)；返回一个 callable_obj
}
"""

sdic_asm = {
    '<_>': [
        {'<comment>': line_str(';')},
        {'<include>': ()},
        {'<head>': ()},
        {'<head>': {'>s_lines<': ("<>", "<comment|token_p>")}},
        {'<asm>': '<comment><include><includelib><symbol><segment>'},
    ],
    '><': base_reg,
    '>s_lines<': base_lines, }

asmload = lambda s: LetxBuild(sdic_asm, 'asm').parse(s)[1]


def __test_asm():
    t0 = '''
'''
    _unittest(parse_asm, (True, t0))


def parse_asm(asm_str):
    ret = asmload(asm_str)
    return ret


# ===============================================================
# ========================== c2goasm FUNC ==========================
# ===============================================================

def c2goasm(in_dir, out_dir):
    pass


def main(default_cmd='all_test', default_in='./php-src', default_out='./go-asm'):
    cmd = sys.argv[1] if len(sys.argv) >= 2 else default_cmd
    in_dir = sys.argv[2] if len(sys.argv) >= 3 else default_in
    out_dir = sys.argv[3] if len(sys.argv) >= 4 else default_out

    if cmd == 'all_test':
        all_test()
    elif cmd == 'clbuild':
        clbuild()
    elif cmd == 'clean_pp':
        clean_pp()
    elif cmd == 'c2goasm':
        c2goasm(in_dir, out_dir)
    else:
        print '''
useage ` python pycl.py all_test | clbuild | clean_pp | c2goasm [in_dir] [out_dir]`

'''


if __name__ == '__main__':
    _LOG("\n==========START===========")
    main()
    _LOG("\n==========END===========")
