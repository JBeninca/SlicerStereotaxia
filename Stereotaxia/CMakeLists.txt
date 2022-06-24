#-----------------------------------------------------------------------------
set(MODULE_NAME Stereotaxia)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  Recursos/__init__.py
  Recursos/gestion_Fiduciarios.py
  Recursos/Maquina_Russell_Brown.py
  Recursos/utilitarios.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/Icons/CTHeadFrame.png
  Resources/Espacio_Marco/Aguja_de_Puncion.vtk
  Resources/Espacio_Marco/Arco.vtk
  Resources/Espacio_Marco/content.txt
  Resources/Espacio_Marco/CoordinateModel.vtk
  Resources/Espacio_Marco/CT-AAA.vp
  Resources/Espacio_Marco/CT-Muscle.vp
  "Resources/Espacio_Marco/Displacement to color.txt"
  Resources/Espacio_Marco/Fantasma_Modelo.vtk
  "Resources/Espacio_Marco/Master Scene View.png"
  Resources/Espacio_Marco/N_Locators.vtk
  Resources/Espacio_Marco/Transformada_angulo_Alfa.h5
  Resources/Espacio_Marco/Transformada_angulo_Beta.h5
  Resources/Espacio_Marco/Transformada_Arruinadora.h5
  Resources/Espacio_Marco/Transformada_Correctora_del_Volumen.h5
  Resources/Espacio_Marco/Transformada_Der_Izq.h5
  Resources/Espacio_Marco/Transformada_Isocentro.h5
  Resources/Espacio_Marco/_Marco_Scene.mrml
  Resources/Espacio_Marco/_Marco_Scene.png
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )
