cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(Stereotaxia)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/JBeninca/SlicerStereotaxia#stereotaxia")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "Dr. Miguel Ibanez, Dr. Dante Lovey, Dr. Lucas Vera, Dr. Elena Zema, Dr. Jorge Beninca, Marc Jermann (FHNW (CH)), Dr. Dorian Vogel (FHNW (CH), LiU (SE))")
set(EXTENSION_DESCRIPTION "Compute stereotactic frame coordinates for neurosurgery planning.")
set(EXTENSION_ICONURL "https://github.com/JBeninca/SlicerStereotaxia/raw/main/Stereotaxia.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/JBeninca/SlicerStereotaxia/raw/main/Screenshot.jpg https://github.com/JBeninca/SlicerStereotaxia/raw/main/resources/Images/Screenshot_02_StereotacticTrajectories.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Stereotaxia)
add_subdirectory(StereotaxiaLite)
add_subdirectory(find_zFrame)
add_subdirectory(stereo_points)
add_subdirectory(probeView)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
