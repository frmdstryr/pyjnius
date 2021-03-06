from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
__all__ = ('autoclass', 'ensureclass','dump_spec','load_spec','build_cache')

from os.path import dirname, join, exists
    
from six import with_metaclass

from jnius.jnius import (
    JavaClass, MetaJavaClass, JavaMethod, JavaStaticMethod,
    JavaField, JavaStaticField, JavaMultipleMethod, find_javaclass
)


class Class(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/Class'

    desiredAssertionStatus = JavaMethod('()Z')
    forName = JavaMultipleMethod([
        ('(Ljava/lang/String,Z,Ljava/lang/ClassLoader;)Ljava/langClass;', True, False),
        ('(Ljava/lang/String;)Ljava/lang/Class;', True, False), ])
    getClassLoader = JavaMethod('()Ljava/lang/ClassLoader;')
    getClasses = JavaMethod('()[Ljava/lang/Class;')
    getComponentType = JavaMethod('()Ljava/lang/Class;')
    getConstructor = JavaMethod('([Ljava/lang/Class;)Ljava/lang/reflect/Constructor;')
    getConstructors = JavaMethod('()[Ljava/lang/reflect/Constructor;')
    getDeclaredClasses = JavaMethod('()[Ljava/lang/Class;')
    getDeclaredConstructor = JavaMethod('([Ljava/lang/Class;)Ljava/lang/reflect/Constructor;')
    getDeclaredConstructors = JavaMethod('()[Ljava/lang/reflect/Constructor;')
    getDeclaredField = JavaMethod('(Ljava/lang/String;)Ljava/lang/reflect/Field;')
    getDeclaredFields = JavaMethod('()[Ljava/lang/reflect/Field;')
    getDeclaredMethod = JavaMethod('(Ljava/lang/String,[Ljava/lang/Class;)Ljava/lang/reflect/Method;')
    getDeclaredMethods = JavaMethod('()[Ljava/lang/reflect/Method;')
    getDeclaringClass = JavaMethod('()Ljava/lang/Class;')
    getField = JavaMethod('(Ljava/lang/String;)Ljava/lang/reflect/Field;')
    getFields = JavaMethod('()[Ljava/lang/reflect/Field;')
    getInterfaces = JavaMethod('()[Ljava/lang/Class;')
    getMethod = JavaMethod('(Ljava/lang/String,[Ljava/lang/Class;)Ljava/lang/reflect/Method;')
    getMethods = JavaMethod('()[Ljava/lang/reflect/Method;')
    getModifiers = JavaMethod('()[I')
    getName = JavaMethod('()Ljava/lang/String;')
    getPackage = JavaMethod('()Ljava/lang/Package;')
    getProtectionDomain = JavaMethod('()Ljava/security/ProtectionDomain;')
    getResource = JavaMethod('(Ljava/lang/String;)Ljava/net/URL;')
    getResourceAsStream = JavaMethod('(Ljava/lang/String;)Ljava/io/InputStream;')
    getSigners = JavaMethod('()[Ljava/lang/Object;')
    getSuperclass = JavaMethod('()Ljava/lang/reflect/Class;')
    isArray = JavaMethod('()Z')
    isAssignableFrom = JavaMethod('(Ljava/lang/reflect/Class;)Z')
    isInstance = JavaMethod('(Ljava/lang/Object;)Z')
    isInterface = JavaMethod('()Z')
    isPrimitive = JavaMethod('()Z')
    newInstance = JavaMethod('()Ljava/lang/Object;')
    toString = JavaMethod('()Ljava/lang/String;')


class Object(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/Object'

    getClass = JavaMethod('()Ljava/lang/Class;')
    hashCode = JavaMethod('()I')


class Modifier(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/reflect/Modifier'

    isAbstract = JavaStaticMethod('(I)Z')
    isFinal = JavaStaticMethod('(I)Z')
    isInterface = JavaStaticMethod('(I)Z')
    isNative = JavaStaticMethod('(I)Z')
    isPrivate = JavaStaticMethod('(I)Z')
    isProtected = JavaStaticMethod('(I)Z')
    isPublic = JavaStaticMethod('(I)Z')
    isStatic = JavaStaticMethod('(I)Z')
    isStrict = JavaStaticMethod('(I)Z')
    isSynchronized = JavaStaticMethod('(I)Z')
    isTransient = JavaStaticMethod('(I)Z')
    isVolatile = JavaStaticMethod('(I)Z')


class Method(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/reflect/Method'

    getName = JavaMethod('()Ljava/lang/String;')
    toString = JavaMethod('()Ljava/lang/String;')
    getParameterTypes = JavaMethod('()[Ljava/lang/Class;')
    getReturnType = JavaMethod('()Ljava/lang/Class;')
    getModifiers = JavaMethod('()I')
    isVarArgs = JavaMethod('()Z')


class Field(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/reflect/Field'

    getName = JavaMethod('()Ljava/lang/String;')
    toString = JavaMethod('()Ljava/lang/String;')
    getType = JavaMethod('()Ljava/lang/Class;')
    getModifiers = JavaMethod('()I')


class Constructor(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = 'java/lang/reflect/Constructor'

    toString = JavaMethod('()Ljava/lang/String;')
    getParameterTypes = JavaMethod('()[Ljava/lang/Class;')
    getModifiers = JavaMethod('()I')
    isVarArgs = JavaMethod('()Z')


def get_signature(cls_tp):
    tp = cls_tp.getName()
    if tp[0] == '[':
        return tp.replace('.', '/')
    signatures = {
        'void': 'V', 'boolean': 'Z', 'byte': 'B',
        'char': 'C', 'short': 'S', 'int': 'I',
        'long': 'J', 'float': 'F', 'double': 'D'}
    ret = signatures.get(tp)
    if ret:
        return ret
    # don't do it in recursive way for the moment,
    # error on the JNI/android: JNI ERROR (app bug): local reference table
    # overflow (max=512)

    # ensureclass(tp)
    return 'L{0};'.format(tp.replace('.', '/'))


registers = []


def ensureclass(clsname):
    if clsname in registers:
        return
    jniname = clsname.replace('.', '/')
    if MetaJavaClass.get_javaclass(jniname):
        return
    registers.append(clsname)
    autoclass(clsname)


def lower_name(s):
    return s[:1].lower() + s[1:] if s else ''


def bean_getter(s):
    return (s.startswith('get') and len(s) > 3 and s[3].isupper()) or (s.startswith('is') and len(s) > 2 and s[2].isupper())


def autoclass(clsname, cached=True):
    jniname = clsname.replace('.', '/')
    cls = MetaJavaClass.get_javaclass(jniname)
    if cls:
        return cls
    
    if cached:
        #: Try to load from cache
        return cached_autoclass(clsname,mem=False) # Ignore mem, we just tried

    classDict = {}

    # c = Class.forName(clsname)
    c = find_javaclass(clsname)
    if c is None:
        raise Exception('Java class {0} not found'.format(c))
        return None

    constructors = []
    for constructor in c.getConstructors():
        sig = '({0})V'.format(
            ''.join([get_signature(x) for x in constructor.getParameterTypes()]))
        constructors.append((sig, constructor.isVarArgs()))
    classDict['__javaconstructor__'] = constructors

    methods = c.getMethods()
    methods_name = [x.getName() for x in methods]
    for index, method in enumerate(methods):
        name = methods_name[index]
        if name in classDict:
            continue
        count = methods_name.count(name)

        # only one method available
        if count == 1:
            static = Modifier.isStatic(method.getModifiers())
            varargs = method.isVarArgs()
            sig = '({0}){1}'.format(
                ''.join([get_signature(x) for x in method.getParameterTypes()]),
                get_signature(method.getReturnType()))
            cls = JavaStaticMethod if static else JavaMethod
            classDict[name] = cls(sig, varargs=varargs)
            if name != 'getClass' and bean_getter(name) and len(method.getParameterTypes()) == 0:
                lowername = lower_name(name[3:])
                classDict[lowername] = (lambda n: property(lambda self: getattr(self, n)()))(name)
            continue

        # multiple signatures
        signatures = []
        for index, subname in enumerate(methods_name):
            if subname != name:
                continue
            method = methods[index]
            sig = '({0}){1}'.format(
                ''.join([get_signature(x) for x in method.getParameterTypes()]),
                get_signature(method.getReturnType()))
            '''
            print 'm', name, sig, method.getModifiers()
            m = method.getModifiers()
            print 'Public', Modifier.isPublic(m)
            print 'Private', Modifier.isPrivate(m)
            print 'Protected', Modifier.isProtected(m)
            print 'Static', Modifier.isStatic(m)
            print 'Final', Modifier.isFinal(m)
            print 'Synchronized', Modifier.isSynchronized(m)
            print 'Volatile', Modifier.isVolatile(m)
            print 'Transient', Modifier.isTransient(m)
            print 'Native', Modifier.isNative(m)
            print 'Interface', Modifier.isInterface(m)
            print 'Abstract', Modifier.isAbstract(m)
            print 'Strict', Modifier.isStrict(m)
            '''
            signatures.append((sig, Modifier.isStatic(method.getModifiers()), method.isVarArgs()))

        classDict[name] = JavaMultipleMethod(signatures)

    for iclass in c.getInterfaces():
        if iclass.getName() == 'java.util.List':
            classDict['__getitem__'] = lambda self, index: self.get(index)
            classDict['__len__'] = lambda self: self.size()
            break

    for field in c.getFields():
        static = Modifier.isStatic(field.getModifiers())
        sig = get_signature(field.getType())
        cls = JavaStaticField if static else JavaField
        classDict[field.getName()] = cls(sig)

    classDict['__javaclass__'] = clsname.replace('.', '/')

    return MetaJavaClass.__new__(
        MetaJavaClass,
        clsname,  # .replace('.', '_'),
        (JavaClass, ),
        classDict)


def dump_spec(clsname, packed=True):
    """ Makes a spec of a JavaClass that can be stored and used passed to load_spec to statically define a JavaClass. 
         Allows avoiding having to load everything via the JNI (which is slow) every time.
         
        @param clsname: dottect object name of java class
        @returns spec
    """

    c = find_javaclass(clsname)
    if c is None:
        raise Exception('Java class {0} not found'.format(c))
        return None
    
    spec = {
        'class': clsname,
        'constructors': {},
        'interfaces': [],
        'fields': {},
        'methods': {},
        #'extends': 'java.lang.Object', # Superclass
    }

    #: Get spec for each constructor
    for constructor in c.getConstructors():
        sig = '({0})V'.format(
            ''.join([get_signature(x) for x in constructor.getParameterTypes()]))
        spec['constructors'][sig] = {
            'vargs':  constructor.isVarArgs(),
            'sig': sig,
        }
    
    #: Get spec for each method
    methods = c.getMethods()
    methods_name = [x.getName() for x in methods]
    for index, method in enumerate(methods):
        name = methods_name[index]
        if name in spec['methods']:
            continue
        count = methods_name.count(name)
        
        spec['methods'][name] = {}
        for index, subname in enumerate(methods_name):
            if subname != name:
                continue
            method = methods[index]
            sig = '({0}){1}'.format(
                ''.join([get_signature(x) for x in method.getParameterTypes()]),
                get_signature(method.getReturnType()))

            mods = method.getModifiers()
            spec['methods'][name][sig] = {
                'vargs': method.isVarArgs(),
                #'public': Modifier.isPublic(mods),
                #'protected':Modifier.isProtected(mods),
                #'private': Modifier.isPrivate(mods),
                'static': Modifier.isStatic(mods),
                #'final': Modifier.isFinal(mods),
                #'synchronized': Modifier.isSynchronized(mods),
                #'volatile': Modifier.isVolatile(mods),
                #'transient': Modifier.isTransient(mods),
                #'native': Modifier.isNative(mods),
                #'abstract': Modifier.isAbstract(mods),
                #'strict': Modifier.isStrict(mods),
                'sig': sig,
                'name': name,
            }

    #: Get spec for each field
    for field in c.getFields():
        mods = field.getModifiers()
        
        spec['fields'][field.getName()] = {
            #'public': Modifier.isPublic(mods),
            #'protected':Modifier.isProtected(mods),
            #'private': Modifier.isPrivate(mods),
            'static': Modifier.isStatic(mods),
            #'final': Modifier.isFinal(mods),
            #'synchronized': Modifier.isSynchronized(mods),
            #'volatile': Modifier.isVolatile(mods),
            #'transient': Modifier.isTransient(mods),
            #'native': Modifier.isNative(mods),
            #'abstract': Modifier.isAbstract(mods),
            #'strict': Modifier.isStrict(mods),
            'name': field.getName(),
            'sig': get_signature(field.getType()),
        }
        
    #: Get spec reference for each interface
    for iclass in c.getInterfaces():
        spec['interfaces'].append(iclass.getName())

    #: Get spec reference for the superclass interface
    #spec['extends'] = c.getSuperclass().getName()
    if packed:
        return pack_spec(spec)
    return spec


def pack_spec(spec):
    """ Tuples load 4x faster than dictionaries so "pack" the dictonary
        into a tuple of tuples.
    """
    methods = []
    for name, specs in spec['methods'].iteritems():
        sigs = [(s['sig'], s['static'], s['vargs']) for s in specs.values()]
        methods.append((name, tuple(sigs)))

    fields = []
    for name, s in spec['fields'].iteritems():
        fields.append((name, s['sig'], s['static']))

    return (
        spec['class'],
        tuple([(c['sig'], c['vargs'])
               for c in spec['constructors'].values()]),
        tuple(spec['interfaces']),
        tuple(methods),
        tuple(fields),
    )

def load_spec(spec):
    """ Loads a JavaClass from a spec. Returns the same output as  autoclass, 
        but instead of using the JNI to build the class via reflection it loads the previously 
        reflected values from the spec, allowing you to "cache" a JavaClass definition.
         
        @param spec: spec dictonary from dump_spec
        @returns JavaClass instance that should equal the autoclass output
    """

    javaclass, constructors, interfaces, methods, fields = spec

    cls = MetaJavaClass.get_javaclass(javaclass.replace('.', '/'))
    if cls:
        return cls
    
    #: Add type and constructors
    attributes = {
        '__javaclass__': javaclass.replace('.','/'),
        '__javaconstructor__': constructors,
    }
    
    #: Add support for any interfaces
    if 'java.util.List' in interfaces:
        #: Update is slow
        attributes['__getitem__'] = lambda self, index: self.get(index)
        attributes['__len__'] = lambda self: self.size()

    #: Add methods
    for name, m in methods:
        if len(m) > 1:
            method = JavaMultipleMethod(list(m))
        else:
            ms = m[0]
            method = (JavaStaticMethod if ms[1] else JavaMethod)(ms[0])
        attributes[name] = method

    #: Add fields
    for f in fields:
        attributes[f[0]] = (JavaStaticField if f[2] else JavaField)(f[1])

    return MetaJavaClass.__new__(
        MetaJavaClass,
        javaclass,
        (JavaClass, ),
        attributes
    )

_CACHE_FILE = join(dirname(__file__),'reflect.javac')
_SPEC_CACHE = {}

def cached_autoclass(clsname, mem=True, save=True, output='msgpack', flush=False):
    """ Attempt to load the class from cache. If it doesn't exist,  
        create the cache.
        
        Cache creates a json file called 'reflect.javac' in this folder.
        
        @param: clsname: JavaClass to load
        @param: mem: Check in memory for class first
        @param: flush: Ignore cache file if one exists
        @param: output: Cache file type to use (pickle or json)
        @param: save: Update/create the cache file if necessary
    """
    #: Try memory first
    global _SPEC_CACHE
    if mem:
        cls = MetaJavaClass.get_javaclass(clsname.replace('.', '/'))
        if cls:
            return cls
    pargs = {}
    if output=='json':
        import json as pickle
    elif output=='msgpack':
        import msgpack as pickle
    else:
        import cPickle as pickle
        pargs = {"protocol": pickle.HIGHEST_PROTOCOL}
        
    #: Try to load from file
    specs = {} if flush else _SPEC_CACHE
    
    if not flush and not specs and exists(_CACHE_FILE):
        with open(_CACHE_FILE,'rb') as f:
            try:
                specs = pickle.load(f)
                _SPEC_CACHE = specs
            except:
                pass #: Warn of failure at least? 
    
    #: If spec cache doesn't exist, create it
    if clsname not in specs:
        #: Create spec
        specs[clsname] = dump_spec(clsname)
        
        #: Save to  javac
        if save:
            try:
                with open(_CACHE_FILE,'wb') as f:
                    pickle.dump(specs, f, **pargs)
            except:
                pass #: Warn of failure at least?
        
    #: Load from spec
    return load_spec(specs[clsname])


def build_cache(clsnames, output='pickle'):
    """ Generates a javac file containing all the JavaClass names given.

    """
    if output=='json':
        import json as pickle
        pargs = {}
    else:
        import cPickle as pickle
        pargs = {"protocol":pickle.HIGHEST_PROTOCOL}

    specs = {n:dump_spec(n,mem=False,save=False,flush=True) for n in clsnames}

    #: Save
    with open(_CACHE_FILE,'w') as f:
        pickle.dump(specs,f,**pargs)

