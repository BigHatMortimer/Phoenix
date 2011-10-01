#---------------------------------------------------------------------------
# Name:        etg/object.py
# Author:      Robin Dunn
#
# Created:     9-Nov-2010
# Copyright:   (c) 2011 by Total Control Software
# License:     wxWindows License
#---------------------------------------------------------------------------

import etgtools
import etgtools.tweaker_tools as tools

PACKAGE   = "wx"   
MODULE    = "_core"
NAME      = "object"   # Base name of the file to generate to for this script
DOCSTRING = ""

# The classes and/or the basename of the Doxygen XML files to be processed by
# this script. 
ITEMS  = [ 
    'wxRefCounter',
    'wxObject',       
#    'wxClassInfo',
]    
    
#---------------------------------------------------------------------------

def run():
    # Parse the XML file(s) building a collection of Extractor objects
    module = etgtools.ModuleDef(PACKAGE, MODULE, NAME, DOCSTRING)
    etgtools.parseDoxyXML(module, ITEMS)
    
    #-----------------------------------------------------------------
    # Tweak the parsed meta objects in the module object as needed for
    # customizing the generated code and docstrings.
    
    
    module.find('wxCreateDynamicObject').ignore()
    
    #module.find('wxClassInfo').abstract = True
    #module.find('wxClassInfo.wxClassInfo').ignore()
    
   
    
    #--------------------------------------------------
    c = module.find('wxRefCounter')
    assert isinstance(c, etgtools.ClassDef)
    c.find('~wxRefCounter').ignore(False)
    c.addPrivateCopyCtor()
    
    
    #--------------------------------------------------
    c = module.find('wxObject')
    c.find('operator delete').ignore()
    c.find('operator new').ignore()
    c.find('GetClassInfo').ignore()
    c.find('IsKindOf').ignore()
    
    # EXPERIMENTAL: By turning off the virtualness of the wxObject dtor, and
    # since there are no other virutals that we are exposing here, then all
    # classes that derive from wxObject that do not have any virtuals of
    # their own can have simpler wrappers generated for them with no extra
    # derived class whose only purpose is to reflect calls to the virtual
    # methods to Python implementations. (And since the only virtual is the
    # dtor then that is of no real benefit to Python code since we're not
    # overriding the dtor anyhow.) In addition it appears that none of these
    # classes would ever need to have Python derived classes anyway. This
    # also makes it easier and less SIP-specific to add or replace ctors in
    # those classes with custom C++ code. (See wxFont and wxAcceleratorTable.)
    c.find('~wxObject').isVirtual = False

    c.addCppMethod('const wxChar*', 'GetClassName', '()',
        body='return self->GetClassInfo()->GetClassName();',
        doc='Returns the class name of the C++ class using wxRTTI.')
    
    c.addCppMethod('void', 'Destroy', '()',
        body='delete self;',
        doc='Deletes the C++ object this Python object is a proxy for.',
        transferThis=True)  # TODO: Check this
        
    # Teach SIP how to convert to specific class types
    c.addItem(etgtools.WigCode("""\
    %ConvertToSubClassCode
        const wxClassInfo* info   = sipCpp->GetClassInfo();
        wxString           name   = info->GetClassName();
        bool               exists = sipFindType(name) != NULL;
        while (info && !exists) {
            info = info->GetBaseClass1();
            name = info->GetClassName();
            exists = sipFindType(name) != NULL;
        }
        if (info) 
            sipType = sipFindType(name);
        else
            sipType = NULL;
    %End
    """))
              
              
    #-----------------------------------------------------------------
    tools.doCommonTweaks(module)
    tools.runGenerators(module)
    
    
#---------------------------------------------------------------------------
if __name__ == '__main__':
    run()

