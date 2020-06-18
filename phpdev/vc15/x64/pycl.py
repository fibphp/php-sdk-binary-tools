#-*- coding: utf-8 -*-
import re
import os
import sys

__all__ = [
    'Error',
    'NotMatchError',
    'ListNotMatchError',
    'letx',
    'base_list',
    'base_reg',
    'base_join',
    'ftoken',
    'fstr'
]

def GBK(s):
    try:
        return s.decode('utf-8').encode('gbk')
    except UnicodeDecodeError as ex:
        return repr(s)

class Error(Exception):
    pass

class NotMatchError(Error):
    def __init__(self, index, msg, obj=None):
        super(NotMatchError, self).__init__(msg)
        self._letx = obj
        self._index = index

class ListNotMatchError(NotMatchError):
    def __init__(self, index, msg, tag_list, ex_list, obj=None):
        super(ListNotMatchError, self).__init__(index, msg, obj)
        self.__dict__.update(dict(zip(tag_list, ex_list)))
        self._index = index
        max_item = max(ex_list, key=lambda i:i._index)
        self._ex = {tag_list[i]:item for (i,item) in enumerate(ex_list) if item._index==max_item._index}

    def __str__(self):
        return '%s >> [ %s ]' % (self.message, ','.join(['<%s> :%s'%(key,item) for (key, item) in self._ex.items()]))


#===============================================================
#========================== MAIN LETX ==========================
#===============================================================

def letx(_sdic, mtag = '_'):
    def add_tag(nk, env, obj):
        assert nk not in env or env[nk] is None, 'comp_letx add_tag:mutil tag %s in %s.' % (nk, env)
        env[nk] = obj

    def comp_letx(s, fdic, env):
        def find_tag(tag_in, env_in=env):
            if not tag_in:
                def _null_parse(index_in, str_in, str_len):
                    index = SKIP_SPACE(index_in, str_in, str_len)
                    return index, ''

                return _null_parse

            tag_in = tag_in[1:] if tag_in[0] == '!' else tag_in
            assert tag_in and tag_in in env_in, 'comp_letx find_tag:can not find(%s) in %s.' % (tag_in, env_in)

            def _pkg_parse(index_in, str_in, str_len):
                assert env_in[tag_in], 'comp_letx _pkg_parse:empty value (%s) in %s.' % (tag_in, env_in)
                parse_func, pkg, _ = env_in[tag_in]
                index, ret_tmp = parse_func(index_in, str_in, str_len)
                ret = pkg(ret_tmp)
                return index, ret
            _pkg_parse.func_name = 'letx %s' % (tag_in, )
            return _pkg_parse

        assert isinstance(s, dict) and len(s)==1, 'comp_letx item:%s must dict and len==1.' % (s, )
        for k, v in s.items():
            assert IS_TAG(k) and '.' not in k, 'comp_letx tag dict item:%s must tag(`.` not in it).' % (k, )
            assert isinstance(v, tuple) and len(v)==2, 'comp_letx tag dict item:%s must tuple and len==2.' % (v, )
            assert hasattr(v[1], '__call__'), 'comp_letx tag dict item:%s[1] must callable.' % (v, )
            main_tag, letx_list, pkg = k[1:-1], v[0], v[1]
            letx_list = [letx_list,] if not isinstance(letx_list, list) else letx_list
            tag_list = []
            for i,item in enumerate(letx_list):
                fix_tag = '%s.%s' % (main_tag, i)
                tag, parse_func = comp_tag(item, fdic, fix_tag, env, find_tag)
                if tag==fix_tag:
                    add_tag(tag, env, (parse_func, DEFAULT_PKG, item))
                tag_list.append(tag)

            func_obj = base_list((main_tag, tag_list), find_tag)
            add_tag(main_tag, env, (func_obj, pkg, letx_list))
            return find_tag(mtag) if main_tag == '_' else find_tag(main_tag)

    def comp_tag(s, fdic, fix_tag, env, find_tag):
        if hasattr(s, '__call__'):
            return fix_tag, s
        elif isinstance(s, (str, unicode, tuple)):
            return comp_tag({'><':s}, fdic, fix_tag, env, find_tag)
        elif isinstance(s, dict):
            assert len(s)==1, 'comp_tag tag|func dict item:%s must len==1.' % (s, )
            for k,v in s.items():
                if IS_FUN(k):
                    assert k in fdic, 'comp_tag func dict item:%s must in fdic:%s.' % (k, fdic)
                    return fix_tag, fdic[k](v, find_tag)
                elif IS_TAG(k):
                    tmp_func = comp_letx(s, fdic, env)
                    return k[1:-1], tmp_func
        else:
            assert False, 'comp_tag item:%s not support.' % (s, )

    def pre_env(s, fix=None):
        def setkey(env, key, val=None):
            if key in env:
                raise TypeError('mutil tag in main_tag:%s' % (s, ))
            else:
                env[key] = val

        env = {}
        if isinstance(s, dict) and len(s)==1:
            for k, ut in s.items():
                if IS_TAG(k):
                    setkey(env, k[1:-1])
                    v, _ = ut
                    v = [v,] if not isinstance(v, list) else v
                    for i,t in enumerate(v):
                        env.update(pre_env(t, '%s_%s_' % (k[1:-1], i)))
                elif fix:
                    setkey(env, fix)
        elif fix:
            setkey(env, fix)
        return env

    assert '<_>' in _sdic and isinstance(_sdic['<_>'], tuple) and \
            len(_sdic['<_>'])==2 and isinstance(_sdic['<_>'][0], list) and \
            hasattr(_sdic['<_>'][1], '__call__'), \
            'input:%s must as {"<_>":([...], lambda x: x)}.' % (_sdic, )
    func_dict = {k:v for k,v in _sdic.items() if IS_FUN(k)}
    main_tag = {'<_>':_sdic['<_>']}
    env = pre_env(main_tag)
    _self = comp_letx(main_tag, func_dict, env)

    return _self

#===============================================================
#========================== HELP FUNC ==========================
#===============================================================

IS_TAG = lambda  k,sa='<',sb='>': len(k)>=2 and k[0]==sa and k[-1]==sb
IS_FUN = lambda  k,sa='>',sb='<': len(k)>=2 and k[0]==sa and k[-1]==sb
IS_REGEXP = lambda  k,sa='</',sb='/>': len(k)>=4 and k[:2]==sa and k[-2:]==sb
IS_REAL = lambda  k,sa='<`',sb='`>': len(k)>=4 and k[:2]==sa and k[-2:]==sb

def DEFAULT_PKG(x):
    return x

def SKIP_SPACE(si, ss, sslen, B={'\n':1, '\r':1, '\t':1, ' ':1}):
    while si<sslen and ss[si] in B:
        si += 1
    return si

def _SPLIT_REG(s, sa='<', sb='>'):
    assert isinstance(s, basestring) and s, '_SPLIT_REG:`%s` is not basestring.' % (s, )
    ret, ib, ia = [], 0, s.find(sa)
    while ia>=0:
        if ia>ib:
            ret.append(s[ib:ia])
        _ia, ib = ia, s.find(sb, ia)+1
        ia = s.find(sa, ia+1)
        assert ia<0 or ia>=ib>_ia, '_SPLIT_REG:`%s` <> not match.' % (s, )
        ret.append(s[_ia:ib])
        if ia<0 and s[ib:]:
            assert s.find(sb, ib)<0, '_SPLIT_REG:`%s` <> not match at end.' % (s, )
            ret.append(s[ib:])

    if not ret:
        ret.append(s)

    return tuple([i.strip() for i in ret if i.strip()])

#===============================================================
#========================= MATCH FUNC ==========================
#===============================================================
class _base(object):
    TestFalse = object()
    debug = False

    def test(self, index, s, sl):
        try:
            index, val = self.__call__(index, s, sl)
            return index, val
        except NotMatchError as ex:
            msg = '%s test NotMatchError:%r @%d<`...%s...`>' % (self, ex, index, s[index-5:index+5])
            return index, self.TestFalse

    def log(self, msg, handle=None):
        if self.debug and msg:
            _msg = msg.replace("\n", r"\n")
            print _msg
            if handle:
                handle.write(_msg+'\n')
                handle.flush()

    def __call__(self, index, s, sl):
        assert index < sl, 'base index:%s out of max_len:%s.'% (index, sl)
        return None, index

    def __repr__(self):
        return '<%s at 0x%08x>' % (str(self), id(self))

    def __str__(self):
        return 'callable letx %s:%s' % (str(self.__class__).split("'")[1].replace('__main__.', ''), getattr(self, '__tag__', 'unknown'))

class base_list(_base):
    def __init__(self, args_tuple, find_tag):
        main_tag, tag_list = args_tuple
        assert main_tag and isinstance(tag_list, (tuple, list)), \
                'base_list `%s` and `%s` must tuple or list.' % (main_tag, tag_list)

        self.func_list = [find_tag(tag) for tag in tag_list]
        self.__tag__ = '<%s>`%s`' % (main_tag, ','.join(tag_list))
        self.main_tag, self.tag_list = main_tag, tag_list

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        if len(self.func_list)==1:
            index, ret = self.func_list[0](index, s, sl)
            return index, ret
        else:
            ex_list = []
            for _, func in enumerate(self.func_list):
                try:
                    index, ret = func(index, s, sl)
                    return index, ret
                except NotMatchError as ex:
                    ex_list.append(ex)
            msg = '%s cannot match @%s<`...%s...`>.' % (str(self), index, s[index-5:index+5])
            raise ListNotMatchError(index, msg, self.tag_list, ex_list, self)

class base_reg(_base):
    def __init__(self, args_tuple_or_str, find_tag):
        args_tuple = _SPLIT_REG(args_tuple_or_str) if isinstance(args_tuple_or_str, basestring) else \
                            args_tuple_or_str
        assert args_tuple and isinstance(args_tuple, tuple), 'base_reg `%s` must tuple.' % (args_tuple, )
        for idx, item in enumerate(args_tuple):
            assert isinstance(item, (str, unicode)), 'base_reg idx %d:`%s` must str or unicode.' % (idx, item)

        tag_split = lambda i:[tag for tag in i[1:-1].split('|')]
        real_split = lambda i:[tag for tag in i[2:-2].split('|') if tag]
        tag_func = lambda i: \
            (re.compile(i[2:-2]), i[2:-2]) if IS_REGEXP(i) else \
            ([real_split(i)]) if IS_REAL(i) else \
            (base_list((i[1:-1], tag_split(i)), find_tag), i[1:-1], i[1:-1][0] == '!') if IS_TAG(i) and '|' in i else \
            (find_tag(i[1:-1]), i[1:-1], i[1:-1] and i[1:-1][0] == '!') if IS_TAG(i) else (i,)

        self.__tag__ = ''.join(args_tuple)
        self.func_list = [tag_func(item) for item in args_tuple if item]
        self.args_tuple = args_tuple

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        ret = []
        for ix, item in enumerate(self.func_list):
            tmp = None
            if len(item) == 3 and item[2]:
                pass
            else:
                index = SKIP_SPACE(index, s, sl)

            if index >= sl:
                break
            if index >= 266:
                pass

            f_len = len(item)
            if f_len==1:
                if isinstance(item[0], (str, unicode)):
                    len_i, tmp_i = len(item[0]), item[0]
                    tmp_str = s[index:index+len_i]
                    if not tmp_str == tmp_i:
                        msg = 'base_reg str %s not math @[%s:%s]<`...%s...`>.'% (tmp_i, index, index+len_i, tmp_str)
                        raise NotMatchError(index, msg, self)
                    else:
                        index += len_i
                        msg = 'base_reg str `%s@%d` >>>%s<<< match @%s<`...%s...`>.'% (GBK(str(self)), ix, GBK(tmp_str), index, GBK(s[index-5:index+5]))
                        self.log(msg)
                else:
                    for tmp_i in item[0]:
                        len_i = len(tmp_i)
                        tmp_str = s[index:index+len_i]
                        if not tmp_str == tmp_i:
                            continue
                        else:
                            index += len_i
                            msg = 'base_reg str `%s@%d` >>>%s<<< match @%s<`...%s...`>.'% (GBK(str(self)), ix, GBK(tmp_str), index, GBK(s[index-5:index+5]))
                            self.log(msg)
                            break
                    else:
                        msg = 'base_reg str %s not math @[%s:%s]<`...%s...`>.'% (tmp_i, index, index+len_i, tmp_str)
                        raise NotMatchError(index, msg, self)

            elif f_len==2:
                reg_tmp, reg_i = item[0].match(s[index:]), item[1]
                tmp = reg_tmp.group() if reg_tmp else None
                if not tmp :
                    msg = 'base_reg reg_exp %s not math @%s<`...%s...`>.'% (reg_i, index, GBK(s[index-5:index+5]))
                    raise NotMatchError(index, msg, self)
                else:
                    index += len(tmp)
                    ret.append(tmp)
                    msg = 'base_reg reg_exp `%s@%d` >>>%s<<< match @%s<`...%s...`>.'% (GBK(str(self)), ix, tmp, index, GBK(s[index-5:index+5]))
                    self.log(msg)
            elif f_len==3:
                index, tmp = item[0](index, s, sl)
                ret.append(tmp)
                msg = 'base_reg tag `%s@%d` >>>%s<<< match @%s<`...%s...`>.'% (GBK(str(self)), ix, tmp, index, GBK(s[index-5:index+5]))
                self.log(msg)
        return index, tuple(ret)




class base_join(_base):
    def __init__(self, args_tuple, find_tag):
        assert isinstance(args_tuple, tuple) and len(args_tuple)==4, \
                'base_join %s must tuple(start, match, split, end).' % (args_tuple, )

        self.func_tuple = [base_reg(item, find_tag) for item in args_tuple]
        self.__tag__ = '%s%s%s...%s' % args_tuple

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        start, match, split, end = self.func_tuple
        T = lambda x: x is self.TestFalse
        b2s = lambda t: '>>>%s<<<' % (t,) if not T(t) else 'not'
        def get_msg(tag, item, t):
            msg = 'base_join %s `%s` %s math @%s<`...%s...`>.'% (tag, str(item), b2s(t), index, s[index-5:index+5])
            self.log(msg) if not T(t) else None
            return msg

        ret = []
        index, is_start = start.test(index, s, sl)
        msg = get_msg('start', start, is_start)
        if T(is_start):
            raise NotMatchError(index, msg, self)

        index, is_end = end.test(index, s, sl)
        while T(is_end):
            index, tmp = match(index, s, sl)
            msg = get_msg('match', match, tmp)
            if T(tmp):
                raise NotMatchError(index, msg, self)

            ret.append(tmp)
            index, is_split = split.test(index, s, sl)
            msg = get_msg('split', split, is_split)
            index, is_end = end.test(index, s, sl)
            msg = get_msg('end', end, is_end)
            if not T(is_end):
                break
            if T(is_split):
                raise NotMatchError(index, msg, self)



        return index, tuple(ret)

def fstr(QUOTES, ESCAPE = '\\'): ##i[si] is " or ', return index of next i[si] without \ before it
    QUOTES = QUOTES.strip()
    def _fstr(index, s, sl):
        if s[index]!=QUOTES:
            msg = 'fstr not start s[%s:]<`...%s...`>,`%s`.'% (index, s[index], QUOTES)
            raise NotMatchError(index, msg, _fstr)
        _index = index+1
        while _index<sl and s[_index] != QUOTES:
            _index += 2 if s[_index]==ESCAPE else 1
        if s[_index] != QUOTES:
            msg = 'fstr not end s[%s:]<`...%s...`>,`%s`.'% (index, s[index], QUOTES)
            raise NotMatchError(__index, msg, _fstr)
        return _index+1, s[index+1:_index]

    return _fstr

def ftoken(END, PRE = None, SKIP = None):
    def _ftoken(index, s, sl):
        while PRE and index < sl and s[index] in PRE:
            index += 1

        if index >= sl:
            msg = 'out of str length %d at %d' % (sl, index)
            raise NotMatchError(index, msg, _ftoken)

        if s[index] in END:
            msg = 'ftoken not start s[%s:]<`...%s...`>,`%s`.'% (index, s[index-5:index+5], s[index])
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

class base_lines(_base):
    def __init__(self, args_tuple, find_tag):
        assert isinstance(args_tuple, tuple) and (len(args_tuple)==2 or len(args_tuple)==3), \
                'base_lines %s must tuple(start, match, [SPLIT_LINE]).' % (args_tuple, )

        self.SPLIT_LINE = args_tuple[2] if len(args_tuple)==3 else True

        args_tuple = args_tuple[:2]
        self.func_tuple = [base_reg(item, find_tag) for item in args_tuple]
        self.__tag__ = '%s -> %s' % args_tuple

    def __call__(self, index, s, sl):
        _, index = super(self.__class__, self).__call__(index, s, sl)

        start, match = self.func_tuple
        F = lambda x: x is self.TestFalse
        b2s = lambda t: '>>>%s<<<' % (t,) if not F(t) else 'not'
        def get_msg(tag, item, t):
            msg = 'base_lines %s `%s` %s math @%s<`...%s...`>.'% (tag, GBK(str(item)), b2s(t), index, GBK(s[index-5:index+5]))
            self.log(msg) if not F(t) else None
            return msg

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
            except NotMatchError as ex:
                break

            msg = get_msg('match', match, tmp)
            if not tmp:
                break

            if index < sl and s[index] == '\n':
                index += 1

            ret.append(tmp)

        return index, tuple(ret)

#===============================================================
#========================== TEST FUNC ==========================
#===============================================================

README = u"""
语法描述为
{<tag>:([tag_item1, tag_item2,...], pkg=lambda x:...)} 依次尝试tag_item,然后pkg结果，tag_item只有一个时，可简写 {<tag>:(tag_item, pkg)}
example
dict{
    <_>: ##  main_tag为<_>, tag中不允许有`.`
        ( [{<tag1>: (sub_tag_items, lambda x:...)}, ## 每一个tag 都为全局变量 find_tag('<tag'>') 可获取此tag的解析函数
           {<tag2>: ({>func<:agrs}, lambda x:...)}, ## 表示调用函数`func`获取结果
           {<tag3>: (agrs, lambda x:...)}, ## func为base_func时可以直接写参数 等同于{<tag3>: ({><:agrs}, lambda x:...)}
           {>func<:agrs}, ## tag可以匿名(补全为上级tag_index_)，等同于{<上级tag_index_>: ({>func<:agrs}, lambda x:x)}
           (agrs), ## 等同于 {<上级tag.index>: ({><:agrs}, lambda x:x)}
           callable_obj, ## callable_obj 参数为(_index当前索引, s原字符串, sl原字符串长度)的可调用对象，匹配则返回结果为 (index下一个带解析处索引,ret获取到的结果)，不匹配raise NotMatchError
            ],
          pkg lambda x:...`) ## 处理tag返回结果的函数
    ><:base_func, ##  base_func为><
    >func<:func, ## func 接受两个参数 (args,find_tag)；返回参数为(_index当前索引, s原字符串, sl原字符串长度)的可调用对象，匹配则返回结果为 (index下一个带解析处索引,ret获取到的结果)，不匹配raise NotMatchError
}
"""

sdic_cl = {
    '<_>':([
            {'<exe>':("<str|token_p>", lambda x: x[0]) },
            {'<define>':(["<`/|-`>D<token_k>=<token_k>", "<`/|-`>D<token_k>"], lambda x: {'define': x}) },
            {'<include>':("<`/|-`>I<str|token_p>", lambda x: {'include': x[0]}) },
            {'<flag>':("<`/|-`><str|token_k>", lambda x: {'flag': x[0]}) },
            {'<zc>':("<`/|-`>Zc:<str|token_k>", lambda x: {'zc': x[0]}) },
            {'<warn>':("<`/|-`>w</[deo1-4]{1}/><str|token_k>", lambda x: {'warn': x}) },
            {'<file>':("<`/|-`>F</[admpRAeori]{1}/><str|token_p>", lambda x: {'file': x}) },
            {'<arg>':("<define|include|file|zc|warn|flag>", lambda x: x[0]) },
            {'<str>':([fstr('"'), fstr("'")], lambda x: x) },
            {'<token_k>':(r"</[\w]+/>", lambda x: x[0])},
            {'<token_p>':(r"</[:.\/\w\\-]+/>", lambda x: x[0])},
            {'<option>':({'>s_lines<':("<>", "<arg>")}, lambda x: {'option': [i[0] for i in x]})},
            {'<input>':({'>s_lines<':("<>", "<str|token_p>")}, lambda x: {'input': [i[0] for i in x]})},
            {'<cl>':("<exe><option><input>", lambda x: x)}
        ], lambda x: x),
    '><':base_reg,
    '>s_lines<':base_lines, }

clload = lambda s: letx(sdic_cl, 'cl')(0, s, len(s))[1]


#===========TEST==========


def _LOG(msg, handle=None):
    print msg
    if handle:
        handle.write(msg+'\n')
        handle.flush()

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

def fix_cl(ret, LIST_KEYS = ['include', 'zc', 'flag'], MAP_KEYS = {'define': lambda df: df if len(df) == 2 else (df[0], None), 'file': lambda df: df, 'warn': lambda df: (df[1], df[0])}):
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

def _test2():
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

def clbuild(test_a = 0, test_s = 0):
    if test_a:
        all_test()
        return

    if test_s:
        return

    t0 = ''
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
    lines = []
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
        define = ' '.join(['/D %s' % (k, ) if v is None else '/D %s=%s' % (k, v) for k, v in item['define'].items()])
        include = ' '.join(['/I "%s"' % (i, ) for i in item['include']])
        zc = ' '.join(['/Zc:%s' % (i, ) for i in item['zc']])
        flag = ' '.join(['/%s' % (i, ) for i in item['flag']]) + " /P "
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
        define = ' '.join(['/D %s' % (k, ) if v is None else '/D %s=%s' % (k, v) for k, v in item['define'].items()])
        include = ' '.join(['/I "%s"' % (i, ) for i in item['include']])
        zc = ' '.join(['/Zc:%s' % (i, ) for i in item['zc']])
        flag = ' '.join(['/%s' % (i, ) for i in item['flag']]) + " /TC /FAs"
        item['file']['a'] = item['file']['o']
        file_f = ' '.join(['/F%s%s' % (k, v) for k, v in item['file'].items()])
        warn = ' '.join(['/w%s%s' % (v, k) for k, v in item['warn'].items()]) + " /wd4090 /wd4047 /wd4146 /wd4244 /wd4267 /wd4216 /wd4018 /wd4113 /wd4101 "

        cmd = r'cl.exe %s %s %s %s %s %s %s' % (define, include, zc, file_f, warn, flag, ' '.join([infile + 'ipp' for infile in item['input']]))
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
        if not l: #  or l.startswith('#pragma') or l.startswith('__pragma'):
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
            #print 'x',
            pass
        else:
            #print '.',
            ret.append(l + "\n")

    with open(outf, 'w') as wf:
        wf.write("/* auto gen by ipp */\n")
        wf.write("\n")
        for i in include:
            wf.write("#include <%s>\n" % (i, ))

        wf.write("\n")
        wf.writelines(ret)

    print "done:", outf, include

def read_lines(f):
    with open(f, 'r') as rf:
        return rf.readlines()

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
        _LOG('\n%s -> %s' %(isPass, func.func_name))
        result = func(*args, **kws)
        import json
        _LOG('=%s' %(json.dumps(result, indent = 2), ))
    except Error as ex:
        _LOG("%s -> %s:%s" %(isPass, type(ex), ex))
        if isPass:
            raise ex
    else:
        if not isPass:
            raise AssertionError("isPass:%s but no Exception!!!"%(isPass))
    return result

def dump_json(f, obj):
    import json
    with open(f, 'w') as wf:
        json.dump(obj, wf, indent = 2)

def load_json(f):
    import json
    with open(f, 'r') as rf:
        return json.load(rf)

def main():
    cmd = sys.argv[1] if len(sys.argv) >= 2 else ''
    if cmd == 'all_test':
        all_test()
    elif cmd == 'clbuild':
        clbuild()
    elif cmd == 'clean_pp':
        clean_pp()
    else:
        print '''
useage `python pycl.py clbuild`

'''

        
if __name__ == '__main__':
    main()
    _LOG("\n==========END===========")
