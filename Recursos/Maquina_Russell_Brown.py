# -*- coding: utf-8 -*-
# Maquina_Russell_Brown version: 21.0504

import numpy
from __main__ import qt, ctk, slicer, vtk


""" Ecuaciones de Russell Brown para tansformacion en 3D
    (not using vtk) -

     El objetivo de este modulo es obtener la matriz de R Brown
     que permite la registracion en coordenadas 3D de un
     marco estereotaxico (Micromar) de una imagen de TAC.

     Luego se calcula un Target en 3D en este en el mismo plano
     (en el mismo corte) en que se ha hecho la registracion.-
     """

class Marco_Micromar():
    """Clase para encapsular datos del marco MICROMAR TM-03B"""
    def __init__(self):
        pass

    # propiedades geometricas del Marco Micromar como clase

    P0 = (0, 0, 0)

    P1 = (130, -70, 0)
    P2 = (130, -70, 0)
    P3 = (130,  70, 140)

    P4 = ( 70, 130, 140)
    P5 = (-70, 130, 0)
    P6 = (-70, 130, 0)

    P7 = (-130,  70, 140)
    P8 = (-130, -70, 0)
    P9 = (-130, -70, 0)

    P = (P0, P1, P2, P3, P4, P5, P6, P7, P8, P9)
    Pts = P
    Pall = P
    P_all = P


class calculus():
    def __init__():
        pass
        
    def Ecuaciones_Russell_Brown(self, fiduciarios_2D):
        """Resolucion algebraica (matricial) con las ecuaciones de Russell Brown.
        La entrada a esta funcion es una lista []
        con los 9  fiduciales (leidos del corte tomografico)
        y la salida es la matriz M de transformacion.
        a través de M cada punto puede ser leído en base a las
        coordenadas 3D del volumen tomográfico
        """
        print("----------- ECUACIONES RUSSELL BROWN --------------")

        marco = Marco_Micromar()
        u, v, w, fraccion_N = self.fiduciarios_a_tabla(fiduciarios_2D)
        x, y, z = 0, 1, 2
    
        # calculo de los valores Z en mmarco.
        print("Z segun N-Locators :")
        print("Z(P2)  = ", fraccion_N[1] * marco.P3[z])
        print("Z(P5)  = ", fraccion_N[2] * marco.P4[z])
        print("Z(P8)  = ", fraccion_N[3] * marco.P7[z], " mm.")
        print()

        F = vtk.vtkMatrix3x3()
        F.SetElement(0, 0, fraccion_N[1] * marco.P3[x] + (1-fraccion_N[1]) * marco.P1[x])
        F.SetElement(0, 1, fraccion_N[1] * marco.P3[y] + (1-fraccion_N[1]) * marco.P1[y])
        F.SetElement(0, 2, fraccion_N[1] * marco.P3[z])
        F.SetElement(1, 0, fraccion_N[2] * marco.P4[x] + (1-fraccion_N[2]) * marco.P6[x])
        F.SetElement(1, 1, fraccion_N[2] * marco.P4[y] + (1-fraccion_N[2]) * marco.P6[y])
        F.SetElement(1, 2, fraccion_N[2] * marco.P4[z])
        F.SetElement(2, 0, fraccion_N[3] * marco.P7[x] + (1-fraccion_N[3]) * marco.P9[x])
        F.SetElement(2, 1, fraccion_N[3] * marco.P7[y] + (1-fraccion_N[3]) * marco.P9[y])
        F.SetElement(2, 2, fraccion_N[3] * marco.P7[z])

        print("esta es matriz F ")
        print(F)

        S = vtk.vtkMatrix3x3()
        S.SetElement(0, 0, u[1])
        S.SetElement(0, 1, v[1])
        S.SetElement(0, 2, w[1])
        S.SetElement(1, 0, u[4])
        S.SetElement(1, 1, v[4])
        S.SetElement(1, 2, w[4])
        S.SetElement(2, 0, u[7])
        S.SetElement(2, 1, v[7])
        S.SetElement(2, 2, w[7])

        print("esta es matriz S")
        print(S)

        S.Invert()
        print("esta es Sinv")
        print(S)

        M = vtk.vtkMatrix3x3()
        M.Multiply3x3(S, F, M)
        M.Transpose()
        print("esta es M")
        print(M)
        return M

    def Analisis_por_ICP(self, From_, To_):
        """Calcula la rotacion y traslacion y ampliacion
        por coordenadas apareadas segun una ecuacion vtk
        que usa menor error por cuadrados medios
        entra dos listas y el resultado es una matriz

        """
        puntos = (0, 2, 3, 5, 6, 8)  # son los fidus utilizados
        x, y, z = (0, 1, 2)          # solo para visualizar las coordenadas

        # ============ create source points ==============
        print("Creating source points...")

        sourcePoints = vtk.vtkPoints()
        sourceVertices = vtk.vtkCellArray()

        for p in puntos:
            ras = From_[p]
            id = sourcePoints.InsertNextPoint(ras)
            sourceVertices.InsertNextCell(1)
            sourceVertices.InsertCellPoint(id)
        #print(p, ras)

        source = vtk.vtkPolyData()
        source.SetPoints(sourcePoints)
        source.SetVerts(sourceVertices)

        #============ create target points ==============

        print("Creating target points...")
        targetPoints = vtk.vtkPoints()
        targetVertices = vtk.vtkCellArray()

        for p in puntos:
            ras = To_[p]
            id = targetPoints.InsertNextPoint(ras)
            targetVertices.InsertNextCell(1)
            targetVertices.InsertCellPoint(id)
        #print(p, ras)

        target = vtk.vtkPolyData()
        target.SetPoints(targetPoints)
        target.SetVerts(targetVertices)

        print("Running ICP ----------------")
        """ ----- Run the Iterative Closes Point algorithm -----"""
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(source)
        icp.SetTarget(target)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfIterations(20)
        icp.StartByMatchingCentroidsOn()
        icp.CheckMeanDistanceOn()  # necesario para ver el resultado
        icp.SetMaximumMeanDistance(.01)
        icp.SetMeanDistanceModeToRMS()
        icp.Modified()
        icp.Update()

        #icpTransformFilter = vtk.vtkTransformPolyDataFilter()
        #icpTransformFilter.SetInputData(source)
        #icpTransformFilter.SetTransform(icp)
        #icpTransformFilter.Update()
        #transformedSource = icpTransformFilter.GetOutput()

        print("no. of iterations =", icp.GetNumberOfIterations())
        print("rms error = ", icp.GetMeanDistance())

        return icp.GetMatrix()

    def Multiplica_punto(self, punto, M):
        punto_3D_out = [0,0,0]
        M.MultiplyPoint(punto, punto_3D_out)
        return punto_3D_out

    def Multiplica_lista_de_puntos(self, lista, Matriz):
        list_out = []
        for punto in lista:
            punto_3D_out = [0,0,0]
            Matriz.MultiplyPoint(punto, punto_3D_out)
            punto_out = self.redondea_punto(punto_3D_out, 2)
            list_out.append(punto_out)
        return list_out

    def Transforma_punto(self, punto, Transfo):
        if len(punto) == 3:
            punto.append(1)
        punto_out = [0, 0, 0, 0]
        Transfo.MultiplyPoint(punto, punto_out)
        return punto_out

    def Transforma_lista_de_puntos(self, lista, Transfo):
        lista_out = []
        for f in lista:
            f_out = Transforma_punto(f, Transfo)
            lista_out.append(f_out)
            return lista_out

    def fiduciarios_a_tabla(self, fidu_2D):
        # pasa fidus a una tabla con variables u, v, w, z """
        u, v, w = [], [], []
        fraccion_N = [0, 0, 0, 0]

        for i in range(len(fidu_2D)):
            u.append(fidu_2D[i][0])
            v.append(fidu_2D[i][1])
            w.append(fidu_2D[i][2])

        # fraccion de z calculado por N-Locators:
        fraccion_N[1] = (v[1]-v[0])/(v[2]-v[0])
        fraccion_N[2] = (u[4]-u[5])/(u[3]-u[5])
        fraccion_N[3] = (v[7]-v[8])/(v[6]-v[8])

        return u, v, w, fraccion_N

    def promedio_puntos(self, lista, sele):
        out = [0, 0, 0]
        for p in sele:
            out[0] += lista[p][0]
            out[1] += lista[p][1]
            out[2] += lista[p][2]
        return [out[0]/len(sele), out[1]/len(sele), out[2]/len(sele)]

    def redondea_punto(self, punto, decimales):
        punto_out = [round(punto[0], decimales),
                    round(punto[1], decimales),
                    round(punto[2], decimales)]
        return punto_out

    def redondea_lista_de_puntos(self, lista_in, decimales):
        from copy import deepcopy
        lista_out = deepcopy(lista_in)
        for punto in lista_out:
            punto[:] = map(lambda x: round(x, decimales), punto)
        return lista_out

