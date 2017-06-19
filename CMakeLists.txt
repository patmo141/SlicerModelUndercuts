cmake_minimum_required(VERSION 2.8.9)

project(UndercutRemover)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/UndercutRemover")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Patrick Moore (Impulse Dental Technologies)")
set(EXTENSION_DESCRIPTION "This Module will use a volumetric label map approac to remove undercuts from the model in the Z-axis direction.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/UndercutRemover.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/UndercutRemover/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
