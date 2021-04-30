# -*- coding: utf-8 -*-
# Estereotaxia_Simplex version 16.1206
# Clase gestion Fiduciarios
from __main__ import qt, ctk, slicer, vtk
from Recursos import Maquina_Russell_Brown
from Recursos import utilitarios as util


class gestion_Fiduciarios():
    """ Esta clase maneja la entrada y lectura de los fiduciarios"""
    def __init__(self):
        self.moduloPath = ""
        self.nombre_Nodo = ""
        self.total_de_Fiduciarios = 1

    def Lectura_Fiduciarios(self, nodo_fidu):
        print("Lectura de los fiduciarios.-")
        fiduciarios_TAC = slicer.util.arrayFromMarkupsControlPoints(nodo_fidu)
        return fiduciarios_TAC.tolist()
      
    def Lectura_Fiduciarios_2(self, nombre, total):
        print("Lectura de los fiduciarios.-")
        self.nombre_Nodo = nombre
        self.total_de_Fiduciarios = total
        nodo_fidu = slicer.util.getNode(self.nombre_Nodo)
        if nodo_fidu is None:
            print("Error! No encuentra el nodo ", self.nombre_Nodo)
            return False
        lista_fidus = []
        for i in range(self.total_de_Fiduciarios):  # toma los 9 primeros fidu
            ras = [0, 0, 0]
            nodo_fidu.GetNthFiducialPosition(i, ras)
            lista_fidus.append([round(ras[0], 2), round(ras[1], 2), round(ras[2], 2)])
        return lista_fidus


    def Marcacion_Fiduciarios(self, nombre, total):
        self.nombre_Nodo = nombre
        self.total_de_Fiduciarios = total
        nodo_fidu = slicer.util.getNode(nombre)
        nodo_fidu.SetLocked(False)
        
        self.interaccion_Markups(nodo_fidu, 1)
        self.mixObservador_2 = slicer.util.VTKObservationMixin()  # agrega observador
        self.mixObservador_2.addObserver(nodo_fidu, nodo_fidu.PointPositionDefinedEvent, self.onFiducialAgregado)
        

    def onFiducialAgregado(self, caller, event):
        """ callback de evaluacion de cada fiduciario luego de marcado """
        nodo_fidu = slicer.util.getNode(self.nombre_Nodo)
        nume_fidu = nodo_fidu.GetNumberOfFiducials()
        print("Markup # ", self.nombre_Nodo, nume_fidu)
        if self.nombre_Nodo == "f":   # corrige el fiduciario a su centroide
            RAS_fidu = [0, 0, 0]
            nodo_fidu.GetNthFiducialPosition(nume_fidu-1, RAS_fidu)
            nodo_volu = util.obtiene_nodo_de_widget("Red")
            fidu_centrado = util.Obtiene_Centro_de_Masa(self, nodo_volu, nume_fidu-1, RAS_fidu,  20, -200)
            # modificacion de la posicion del fiduciario
            nodo_fidu.SetNthControlPointPositionFromArray(nume_fidu-1, fidu_centrado[:3])
        if nume_fidu == self.total_de_Fiduciarios:  # se terminó la colecta
            #self.remueveObservador()
            self.mixObservador_2.removeObservers()
            nodo_fidu.SetLocked(True)
            print("Se termina de registrar el/los fiduciarios de :", self.nombre_Nodo) 
            self.interaccion_Markups(nodo_fidu, 0)  # finaliza interaccion
            nodo_fidu.InvokeEvent(1000)  # para lector de eventos a MAIN
            

    def interaccion_Markups(self, nodo_markups, activo):
        #  activo = 1 para interactuar 0 para no
        nodo_logi = slicer.modules.markups.logic()
        nodo_logi.SetActiveListID(nodo_markups)
        nodo_sele = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        nodo_sele.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        nodo_interac = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        nodo_interac.SetPlaceModePersistence(activo)
        nodo_interac.SetCurrentInteractionMode(activo)

    
    """
    def agregaObservador(self):
        print("vino a agrega Scene observador")
        for fiducialLista in slicer.util.getNodes('vtkMRMLMarkupsFiducialNode*').values():
            tag = fiducialLista.AddObserver(fiducialLista.PointPositionDefinedEvent, self.onFiducialAgregado)
            self.observadores_Tags.append((fiducialLista, tag))


    def remueveObservador(self):
            print("vino a remueve Scene observador")  
            for obj, tag in self.observadores_Tags:
                obj.RemoveObserver(tag)
            self.observadores_Tags = []
    """

    def Inicializa_nodo(self, nombre_Nodo):
        self.Borra_nodo(nombre_Nodo)  # intenta borrar nodo anterior
        nodo = self.Genera_nodo(nombre_Nodo)  # sin puntos fiduciarios
        #print("ha generado = ", nodo.GetName())
        return nodo

    def Borra_nodo(self, nombre_Nodo):
        try:
            nodo = slicer.util.getNode(nombre_Nodo)
            if nodo.IsA("vtkMRMLMarkupsFiducialNode"):
                slicer.mrmlScene.RemoveNode(nodo)
                print("ha borrado =", nombre_Nodo)
            else:
                print("no es fiducial node.")
        except:
            print("ha fallado en borrar nodo =", nombre_Nodo)

    def Borra_nodos_por_clase(self, nombre_Nodo):
        nodos = slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
        for nodo in nodos:   # borra nodos antiguos
            if nodo.GetName() == nombre_Nodo:
                slicer.mrmlScene.RemoveNode(nodo)
                print("ha borrado nodo =", nodo.GetName())

    def Genera_nodo(self, nombre_Nodo):
        nodo = slicer.vtkMRMLMarkupsFiducialNode()
        nodo.SetName(nombre_Nodo)
        nodo.SetScene(slicer.mrmlScene)
        slicer.mrmlScene.AddNode(nodo)
        print("ha generado fiducial nodo =", nombre_Nodo)
        return nodo

    def Carga_nodo(self, nombre_Nodo):
        # cargo un archivo vacio, ya que no puedo crearlos
        nodo = slicer.util.loadMarkups(self.moduloPath + "/Espacio Simplex/vacio.mrk.json")
        print("ha cargado markups = ", nombre_Nodo)
        return nodo     

    def Borra_puntos_fiduciarios(self, nombre_Nodo):
        nodo = slicer.util.getNode(nombre_Nodo)
        nodo.RemoveAllMarkups()
        print("se removieron los markups de= ", nombre_Nodo)
        
