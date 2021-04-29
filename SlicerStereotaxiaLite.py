# -*- coding: utf-8 -*-
# SlicerStereotaxiaLite version 21.0422
import os
import logging
import math
import time
import ast   # para eval seguras
from importlib import reload

from __main__ import qt, ctk, slicer, vtk
from slicer.ScriptedLoadableModule import *

from Recursos import Maquina_Russell_Brown
from Recursos import utilitarios as util
from Recursos import gestion_Fiduciarios 

reload(Maquina_Russell_Brown)
reload(util)
reload(gestion_Fiduciarios)

# TODO revisar angulo alfa en cuadrante izquierdo

class SlicerStereotaxiaLite(ScriptedLoadableModule):
    """ Este modulo calcula en el mismo plano de un corte
        tomografico, los 9 fiduciarios y el Target. 
        Usa solamente las ecuaciones de Russel Brown para la 
        determinacion 3D de un sistema de localizadores N 
        de un marco Micromar
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SlicerStereotaxiaLite"
        self.parent.categories = ["Stereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dr. Miguel Ibanez; Dr. Dante Lovey; Dr. Lucas Vera; Dra. Elena Zema; Dr. Jorge Beninca."]
        self.parent.helpText = "Esta es la Version 21.0315"
        self.parent.acknowledgementText = " Este modulo fue desarrollado originalmente por Jorge A.Beninca, durante los meses de Enero a Julio 2015, en el dpto de Neurocirugia del Hospital de Ninos Dr. Orlando Alassia."


class SlicerStereotaxiaLiteWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available
    """
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.Registracion_Bton = ctk.ctkCollapsibleButton()
        self.Registracion_Bton.text = "Registración y cálculo del Target"
        self.Registracion_Bton.collapsed = False
        self.layout.addWidget(self.Registracion_Bton)
        self.Grilla1 = qt.QGridLayout(self.Registracion_Bton)
        self.Resultados_Bton = ctk.ctkCollapsibleButton()
        self.Resultados_Bton.text = "Resultados"
        self.Resultados_Bton.collapsed = False
        self.layout.addWidget(self.Resultados_Bton)
        self.Grilla2 = qt.QGridLayout(self.Resultados_Bton)
        
        self.Bton1 = qt.QPushButton("Inicializa")
        self.Bton2 = qt.QPushButton("Registración ")
        self.Bton3 = qt.QPushButton("Target ")
        self.Bton4 = qt.QPushButton("Entry ")
        self.Bton5 = qt.QPushButton("Guarda la Sesión")
        self.Bton6 = qt.QPushButton("Prueba ")
        
        #self.linea = qt.QLine(0, 0, 100, 0)

        self.Lbl1 = qt.QLabel("")
        self.Lbl1.setAlignment(qt.Qt.AlignCenter)
        self.Lbl2 = qt.QLabel("")
        self.Lbl3 = qt.QLabel("")
        self.Lbl4 = qt.QLabel("")
        self.Lbl5 = qt.QLabel("")
        
        self.Ledit = qt.QLineEdit("Output: ")
        self.textEdit = qt.QTextEdit("")
        self.textEdit.setMaximumSize(500, 200)

        self.Grilla1.addWidget(self.Lbl1, 1, 0)
        #self.Grilla1.addWidget(self.Bton1, 3, 0)
        self.Grilla1.addWidget(self.Bton2, 4, 0)
        self.Grilla1.addWidget(self.Bton3, 5, 0)
        self.Grilla1.addWidget(self.Bton4, 6, 0)
        self.Grilla1.addWidget(self.Bton5, 7, 0)
        self.Grilla1.addWidget(self.Bton6, 15, 0)
        #self.Grilla1.addWidget(self.linea, 8, 0)
        #self.Grilla1.addWidget(self.Ledit, 8, 0)
        self.Grilla1.addWidget(self.Lbl2, 9, 0)
        #self.Grilla1.addWidget(self.Lbl3, 10, 0)
        #self.Grilla1.addWidget(self.Lbl4, 11, 0)
        #self.Grilla1.addWidget(self.Lbl5, 12, 0)
        self.Grilla2.addWidget(self.textEdit, 13, 0)
        
        self.layout.addStretch(1)   # Add vertical spacer
        #
        # conecciones con las clases logicas
        #
        self.Bton1.clicked.connect(lambda: self.selectora_botones("Inicializa"))
        self.Bton2.clicked.connect(lambda: self.selectora_botones("Registracion"))
        self.Bton3.clicked.connect(lambda: self.selectora_botones("Target"))
        self.Bton4.clicked.connect(lambda: self.selectora_botones("Entry Point"))
        self.Bton5.clicked.connect(lambda: self.selectora_botones("Guarda"))
        self.Bton6.clicked.connect(lambda: self.selectora_botones("Pruebas"))
                
        
    def limpia_widget(self):
        self.textEdit.setPlainText("")

    def actualiza_widget(self, param, event):
        print("vino al callback actualiza widget !!!!!!!!!!!")
        print(event)
        #print(param.GetParameterNames())
        self.textEdit.setPlainText("Resultados :")
        self.textEdit.append("")
        self.textEdit.append("Target = " +  param.GetParameter("Target"))
        self.textEdit.append("Entry = " +  param.GetParameter("T_Entry"))
        self.textEdit.append("Trayectoria = " + param.GetParameter("Path_length") + " mm.")
        self.textEdit.append("angulo Alfa = " + param.GetParameter("Target_Angulo_Alfa") )
        self.textEdit.append("angulo Beta = " + param.GetParameter("Target_Angulo_Beta") )
        
    def selectora_botones(self, modo):
        if modo == "Inicializa":
            registracionLogic().Inicializa_Escena()  
            pass
        elif modo == "Registracion":
            nodo_volu = util.obtiene_nodo_de_widget("Red")
            if nodo_volu == None:
                texto = "ERROR: no hay volumenes cargados"
                slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
                return
            self.limpia_widget()
            registracionLogic().grafica_path(False)
            util.cambia_window_level("Red", 100, 50)
            registracionLogic().Inicializa_Escena()
            param = slicer.util.getNode("Param_data")
            self.mixObservador_4 = slicer.util.VTKObservationMixin()
            self.mixObservador_4.addObserver(param, vtk.vtkCommand.AnyEvent, self.actualiza_widget)
            registracionLogic().Obtiene_9_Fiduciarios_f()
        elif modo == "Entry Point":
            self.limpia_widget()
            registracionLogic().grafica_path(False)
            util.cambia_window_level("Red", 100, 50)
            registracionLogic().Obtiene_1_Fiduciario_Entry()
        elif modo == "Target":
            self.limpia_widget()
            registracionLogic().grafica_path(False)
            util.cambia_window_level("Red", 100, 50)
            registracionLogic().Obtiene_1_Fiduciario_Target()
        elif modo == "Guarda":
            registracionLogic().save()
        
        elif modo == "Pruebas":
            print("vino a prueba")
            pass
    
    ###### comienza acción ##########
    registracionLogic().Establece_Escena()
    registracionLogic().Inicializa_Escena()  
        

class registracionLogic(ScriptedLoadableModuleLogic):
    """Esta clase implemtenta todos los computos de registracion y calculo que requiere el modulo"""
    def __init__(self):
        self.gest = gestion_Fiduciarios.gestion_Fiduciarios()
        self.maqui = Maquina_Russell_Brown
        self.modulo = slicer.util.modulePath("SlicerStereotaxiaLite")
        self.rootPath = slicer.mrmlScene.GetRootDirectory()
        self.moduloPath = os.path.split(self.modulo)[0]
        self.archivoPath = self.moduloPath + "/Archivo"
        self.escenaPath = self.moduloPath + "/Espacio_Marco/_Marco_Scene.mrml"

    def Establece_Escena(self):
        print("------------------------------------------------")
        print("            Abre una sesion")
        print("------------------------------------------------")
        print("root path: ", self.rootPath)
        print("modulo: ", self.modulo)
        print("modulo path:", self.moduloPath)
        print("escena en uso: ", self.escenaPath)
        lay = slicer.app.layoutManager()
        lay.setLayout(6)  # red panel
        
    def Inicializa_Escena(self):
        print("------------------------------------------------")
        print("       Genera nodos en una Escena ya abierta")
        print("------------------------------------------------")
        
        # centra el volumen y aproxima a zero
        #print("El volumen con que se trabaja es = ", nodo_volu.GetName())
        #print("el origen del volumen es =")
        #print(nodo_volu.GetOrigin())
        #util.modifica_origen_de_volumen(nodo_volu, [100,100,-100])
        
        util.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        util.centra_nodo_de_widget("Red")
        
        util.Borra_nodos_por_clase("vtkMRMLMarkupsFiducialNode")
        util.Borra_nodos_por_clase("vtkMRMLMarkupsLineNode")
        util.impri_layout_2D("Red", "", 0)
        
        param = util.Genera_Nodo("vtkMRMLScriptedModuleNode", "Param_data")
        #param.SetParameter("Fiduciarios_Marco", str(Maquina_Russell_Brown.Marco_Micromar.P[1:9]))  
        param.SetParameter("Target", str([0.0, 0.0, 0.0]))
        param.SetParameter("T_Entry", str([0.0, 0.0, 0.0]))
        param.SetParameter("Registered_flag", "False")
        
    
    def Obtiene_9_Fiduciarios_f(self):
        print("vino a marcacion de 9 fiduciarios")
        nodo_volu = util.obtiene_nodo_de_widget("Red")
        param = slicer.util.getNode("Param_data")
        param.SetParameter(" Nombre_del_Paciente", nodo_volu.GetName())
        transformada = util.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        nodo_volu.SetAndObserveTransformNodeID(transformada.GetID())
    
        self.gest.moduloPath = self.moduloPath  
        self.gest.Inicializa_nodo("Target")
        self.gest.Inicializa_nodo("Entry")
        nodo_fidu = self.gest.Inicializa_nodo("f")
        nodo_fidu.SetAndObserveTransformNodeID(transformada.GetID())
        
        nodo_fidu.GetDisplayNode().SetGlyphType(1)
        nodo_fidu.GetDisplayNode().SetSelectedColor(0.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 0.0, 0.0)
            
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("f", 9)
            
    def Obtiene_1_Fiduciario_Target(self):
        print("vino a marcacion de 1 Target")
        param = slicer.util.getNode("Param_data")
        if param.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Target sin Registrar previamente!!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        nodo_fidu = self.gest.Inicializa_nodo("Target")
        nodo_fidu.GetDisplayNode().SetGlyphType(2)
        nodo_fidu.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 1.0, 0.0)
        
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("Target", 1)

    def Obtiene_1_Fiduciario_Entry(self):
        print("vino a marcacion de 1 Entry")
        param = slicer.util.getNode("Param_data")
        if param.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Entry sin Registrar previamente!!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        nodo_fidu = self.gest.Inicializa_nodo("Entry")
        nodo_fidu.GetDisplayNode().SetGlyphType(2)
        nodo_fidu.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 1.0, 0.0)
        
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("Entry", 1)

    def main(self, obj, evento):  # funcion principal MAIN del procesamiento de fiduciarios
        print("vino a callback main desde :", type(obj), evento)
        if evento != "UserEvent":
            texto = "No viene a MAIN desde donde debiera !" + str(evento)
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None, **kwargs)
            return
        
        self.mixObservador_1.removeObservers()      
        param = slicer.util.getNode("Param_data")
        #
        #                       procedimiento de REGISTRACION
        #
        if self.gest.nombre_Nodo == "f":
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            fiduciarios_TAC = self.gest.Lectura_Fiduciarios(nodo_fidu)
            matriz_RB = self.maqui.Ecuaciones_Russell_Brown(fiduciarios_TAC)
            array_M_RB = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            fiduciarios_3D = Maquina_Russell_Brown.Multiplica_lista_de_puntos(fiduciarios_TAC, matriz_RB)
         
            matriz_4x4  = self.maqui.Analisis_por_ICP(fiduciarios_TAC, fiduciarios_3D)
            array_M_3D = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            
            transformada = vtk.vtkTransform()
            transformada.SetMatrix(matriz_4x4)

            nodo = slicer.util.getNode("Transformada_Correctora_del_Volumen")
            nodo.SetAndObserveTransformToParent(transformada)
            util.centra_nodo_de_widget("Red")

            param.SetParameter("Fiduciarios_TAC", str(util.redondea_lista_de_puntos(fiduciarios_TAC, 2)))
            param.SetParameter("Array_Matrix_RB", str(array_M_RB))
            param.SetParameter("Registered_flag", "True")
            param.SetParameter("Fiduciarios_3D", str(util.redondea_lista_de_puntos(fiduciarios_3D, 2)))
            param.SetParameter("Array_Matrix_3D", str(array_M_3D))
            param.SetParameter("Target", str([0.0, 0.0, 0.0]))
            param.SetParameter("T_Entry", str([0.0, 0.0, 0.0]))
            param.SetParameter("Transformada_Position", str(util.redondea(transformada.GetPosition(), 2)))
            param.SetParameter("Transformada_Orientation", str(util.redondea(transformada.GetOrientation(), 2)))

            print("Fiduciarios_TAC = " + param.GetParameter("Fiduciarios_TAC"))
            print("Matrix_RB = ", matriz_RB)
            print("Matriz 4x4 = ", matriz_4x4)
            print("Position= ", param.GetParameter("Transformada_Position" ))
            print("Orientation= ", param.GetParameter("Transformada_Orientation"))
            print("Registered_flag = ", param.GetParameter("Registered_flag"))

        elif self.gest.nombre_Nodo == "Target":   # procedimiento del Target
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Target = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo termino
            param.SetParameter("Target", str(util.redondea(Target, 1)))
            self.grafica_path(True)

            texto = "Target = " + param.GetParameter("Target")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            util.impri_layout_2D("Red", texto, 2)
        
            print()
            print("-------------------------------------------")
            print(texto)
            print("-------------------------------------------")
            
        elif self.gest.nombre_Nodo == "Entry":   # procedimiento del Target
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Entry = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo termino
            param.SetParameter("T_Entry", str(util.redondea(Entry, 1)))
            self.grafica_path(True)    

            texto = "Entry = " + param.GetParameter("T_Entry")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            util.impri_layout_2D("Red", texto, 7)
            
            print()
            print("-------------------------------------------")
            print(texto)
            print("-------------------------------------------")

    def grafica_path(self, modo):
        print("vino a grafica path")
        if modo == False:
            util.Borra_nodo("Path")
            return

        param = slicer.util.getNode("Param_data")
        Target = ast.literal_eval(param.GetParameter("Target"))
        Entry = ast.literal_eval(param.GetParameter("T_Entry"))
        
        if Entry[2] == 0 or Target[2] ==0:
            return
        if Entry == Target:
            return
        if (Entry[0]>=0) != (Target[0]>=0):   #(a>0) == (b>0)  
            texto = "ATENCION: el PATH atraviesa la línea media !  "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)

        Alfa, Beta = util.calcula_angulos(Entry, Target)
        largo_path = util.grafica_linea(Entry, Target)
        
        param.SetParameter("Path_length", str(round(largo_path, 2)))
        param.SetParameter("Target_Angulo_Alfa", str(round(Alfa, 2)))
        param.SetParameter("Target_Angulo_Beta", str(round(Beta, 2)))
        
        if Entry[0] >= 0:
            param.SetParameter("Target_Izq_Der_flag", str(True))
        else:
            param.SetParameter("Target_Izq_Der_flag", str(False))
        
        texto = "Alfa : " + param.GetParameter("Target_Angulo_Alfa")
        texto = texto + ",  Beta : "+ param.GetParameter("Target_Angulo_Beta") 
        texto = texto + ", long : " + param.GetParameter("Path_length")
        util.impri_layout_2D("Red", texto, 3)

        print("ángulo_Alfa = ", param.GetParameter("Target_Angulo_Alfa"), "grados.")  #plano lateral
        print("ángulo_Beta = ", param.GetParameter("Target_Angulo_Beta"), "grados.") # plano frotal 
        print("longitud del path = ", param.GetParameter("Path_length"), "mm.")

    def save(self):
        print("vino a save")
        # Create a new directory where the scene will be saved into
        ref_time = time.strftime("%Y%m%d-%H%M%S")
        sceneSaveDirectory = self.moduloPath + "/Archivo/Escena_" + ref_time
        if not os.access(sceneSaveDirectory, os.F_OK):
            os.makedirs(sceneSaveDirectory)
        # Save the scene
        if slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(sceneSaveDirectory, None):
            logging.info("Scene saved to: {0}".format(sceneSaveDirectory))
        else:
            logging.error("Scene saving failed")
        
        # Save los parametros
        param = slicer.util.getNode("Param_data")
        param.SetParameter(" Referencia_tiempo", ref_time)
        dictio = {}
        for item in param.GetParameterNames():
            dictio[item] = param.GetParameter(item)
        import json
        #json.dump(dictio, sceneSaveDirectory + "/parametros.json")   
        js = json.dumps(dictio)
        # Open new json file if not exist it will create
        fp = open(sceneSaveDirectory + "/Parametros_" + ref_time + ".json", 'a')
        # write to json file
        fp.write(js)
        # close the connection
        fp.close()

