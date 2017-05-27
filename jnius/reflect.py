from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
__all__ = ('autoclass', 'ensureclass','dump_spec','load_spec')

import json
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


def autoclass(clsname, cached=False):
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
    
def dump_spec(clsname):
    """ Makes a spec of a JavaClass that can be stored and used passed to load_spec to statically define a JavaClass. 
         Allows avoiding having to load everything via the JNI (which is slow) every time.
         
        @param clsname: dottect object name of java class
        @returns spec: a dictionary of the format:
            {
                'class':clsname,
                'constructors': {
                    'sig1': {constructor spec..},
                    # etc.. 
                },
                'interfaces': [
                    # name
                ],
                'fields':{
                    'name': {field spec...},
                    # etc...
                },
                'methods':{
                    'name': {
                            'sig1': {method spec..},
                            'sig2': {method spec..},
                            # etc ... 
                        },
                    'name2': {},
                    # etc ...
                },
                'extends': 'java.lang.Object', # Superclass
            }
    """

    c = find_javaclass(clsname)
    if c is None:
        raise Exception('Java class {0} not found'.format(c))
        return None
    
    spec = {
        'class':clsname,
        'constructors': {},
        'interfaces': [],
        'fields':{},
        'methods':{},
        'extends': 'java.lang.Object', # Superclass
    }

    #: Get spec for each constructor
    for constructor in c.getConstructors():
        sig = '({0})V'.format(
            ''.join([get_signature(x) for x in constructor.getParameterTypes()]))
        spec['constructors'][sig] = {
            'vargs':  constructor.isVarArgs(),
            'signature': sig,
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
                'public': Modifier.isPublic(mods),
                'protected':Modifier.isProtected(mods),
                'private': Modifier.isPrivate(mods),
                'static': Modifier.isStatic(mods),
                'final': Modifier.isFinal(mods),
                'synchronized': Modifier.isSynchronized(mods),
                'volatile': Modifier.isVolatile(mods),
                'transient': Modifier.isTransient(mods),
                'native': Modifier.isNative(mods),
                'abstract': Modifier.isAbstract(mods),
                'strict': Modifier.isStrict(mods),
                'signature': sig,
                'name': name,
            }

    #: Get spec for each field
    for field in c.getFields():
        mods = field.getModifiers()
        
        spec['fields'][field.getName()] = {
            'public': Modifier.isPublic(mods),
            'protected':Modifier.isProtected(mods),
            'private': Modifier.isPrivate(mods),
            'static': Modifier.isStatic(mods),
            'final': Modifier.isFinal(mods),
            'synchronized': Modifier.isSynchronized(mods),
            'volatile': Modifier.isVolatile(mods),
            'transient': Modifier.isTransient(mods),
            'native': Modifier.isNative(mods),
            'abstract': Modifier.isAbstract(mods),
            'strict': Modifier.isStrict(mods),
            'name': field.getName(),
            'signature': get_signature(field.getType()),
        }
        
    #: Get spec reference for each interface
    for iclass in c.getInterfaces():
        spec['interfaces'].append(iclass.getName())

    #: Get spec reference for the superclass interface
    #spec['extends'] = c.getSuperclass().getName()
    
    return spec

def load_spec(spec):
    """ Loads a JavaClass from a spec. Returns the same output as  autoclass, 
        but instead of using the JNI to build the class via reflection it loads the previously 
        reflected values from the spec, allowing you to "cache" a JavaClass definition.
         
        @param spec: spec dictonary from dump_spec
        @returns JavaClass instance that should equal the autoclass output
    """
    cls = MetaJavaClass.get_javaclass(spec['class'].replace('.', '/'))
    if cls:
        return cls
    
    #: Add type and constructors
    attributes = {
        '__javaclass__': spec['class'].replace('.','/'),
        '__javaconstructor__':   [(c['signature'],c['vargs']) 
                                                    for c in spec['constructors'].values()],
    }
    
    #: Add support for any interfaces
    if 'java.util.List' in spec['interfaces']:
        attributes.update({
            '__getitem__': lambda self, index: self.get(index),
            '__len__': lambda self: self.size()
        })
        
    #: Add methods
    attributes.update({
            name: JavaMultipleMethod(
                                [(ms['signature'], ms['static'], ms['vargs']) for ms in m.values()]
                            )  if len(m)>1 else (
                                JavaStaticMethod if m.values()[0]['static'] else JavaMethod
                            )(m.values()[0]['signature'])
        for name,m in spec['methods'].items()
    })
    
    #: Add fields
    attributes.update({
        f['name']:(JavaStaticField if f['static'] else JavaField)(f['signature'])
        for f in spec['fields'].values()
    })
    
    return MetaJavaClass.__new__(
        MetaJavaClass,
        spec['class'], 
        (JavaClass, ),
        attributes
    )

def cached_autoclass(clsname,mem=True,flush=False):
    """ Attempt to load the class from cache. If it doesn't exist,  
        create the cache.
        
        Cache creates a json file called 'reflect.javac' in this folder.
        
        @param: clsname: JavaClass to load
        @param: mem: Check in memory for class first
        @param: flush: Ignore cache file if one exists
    """
    #: Try memory first
    if mem:
        cls = MetaJavaClass.get_javaclass(clsname.replace('.', '/'))
        if cls:
            return cls
        
    #: Try to load from file
    specs = {}
    javac = join(dirname(__file__),'reflect.javac')
    if exists(javac) and not flush:
        with open(javac,'r') as f:
            try:
                specs = json.load(f)
            except:
                pass #: Warn of failure at least? 
    
    #: If spec cache doesn't exist, create it
    if clsname not in specs:
        #: Create spec
        specs[clsname] = dump_spec(clsname)
        
        #: Save to  javac
        try:
            with open(javac,'w') as f:
                json.dump(specs,f,indent=2)
        except:
            pass #: Warn of failure at least?     
        
    #: Load from spec
    return load_spec(specs[clsname])
    
    
    
    
    
    

    