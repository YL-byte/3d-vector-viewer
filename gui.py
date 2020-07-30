from tkinter import *
from PIL import ImageTk, Image
from vectors import Vector, Triangle, radiansToDegrees
import numpy as np

class App(Frame):
    def __init__(self, master=Tk(), width=500, height=500, x_axis_scale=100, y_axis_scale=100, zoom=100, drag_scale=0.01):

        #App and windows settings
        Frame.__init__(self, master)
        self.master = master
        master.title("3D viewer - tkinter and numpy")
        self.width = width
        self.height = height

        #Bind mouse to Camera Angle
        self.master.bind('<Key>', lambda e: self.keyPress(e))#KeyRelease
        self.master.bind('<KeyRelease>', lambda e: self.keyRelease(e))  # KeyRelease
        self.master.bind('<Button-1>', lambda e :self.clickScreen(e))
        self.master.bind('<B1-Motion>', lambda e: self.dragScreen(e))
        self.game_canvas = Canvas(master, height=self.height, width=self.width, bg='grey')
        self.all_vectors = []

        #3d person viewing settings
        self.x_axis_scale = x_axis_scale #How much to scale the screen X axis
        self.y_axis_scale = y_axis_scale #How much to scale the screen Y axis
        self.zoom = zoom
        self.root_point = np.array([self.width / 2, self.height / 2]) #Where the (0,0) of the screen X and Y axis is located
        self.drag_scale = drag_scale #How Sensitive the changes to the mouse drag

        #Where camera is located in the game world
        self.camera_vector = Vector([0,0,0],[0,0,1], display_on_screen=False, color='Blue')
        self.camera_moving_vel = 1 #When the player wants to move the camera
        self.view_angle = 2 * np.pi / 3 #Equals 2*theta

        #Where player clicks on the screen canvas
        self.screen_x = 0
        self.screen_y = 0
        self.camera_distance_from_character = 10 #In pixals

        #What the X and Y vectors on the screen represent in the game
        self.screen_x_vector = Vector([0,0,0],[1,0,0], display_on_screen=False, color='red') #What the X axis of the monitor represents
        self.screen_y_vector = Vector([0,0,0],[0,1,0], display_on_screen=False, color='green') #What the Y axis of the monitor represents

    def clickScreen(self, e):
        self.screen_x = e.x
        self.screen_y = e.y

    def dragScreen(self, e):
        #Update vector according to drag
        self.camera_vector.updateVector()
        self.camera_vector.normalizeVector()
        diff_x = e.x - self.screen_x
        diff_y = e.y - self.screen_y

        #The camera vector rotates around the screen_x_vector with diff_y and around the screen_y_vector with diff_x

        #The camera is perpendicular to the XY plane
        self.camera_vector.vector = np.cross(self.screen_x_vector.vector, self.screen_y_vector.vector)

        # Unitize the vectors
        self.screen_x_vector.normalizeVector()
        self.screen_y_vector.normalizeVector()

        #Modify all vectors according to the screen drage
        self.modifyVectors(diff_x, diff_y)

        #Assign current x, y to where the player last clicked
        self.screen_x = e.x
        self.screen_y = e.y

    def keyPress(self, e):
        print (e.char, 'Press')
        #Walk forward
        if e.char == 'w' or e.char == 'W':
            self.modifyVectors(move_y=1)

        #Walk backwards
        elif e.char == 's' or e.char == 'S':
            self.modifyVectors(move_y=-1)

        #Walk left
        elif e.char == 'a' or e.char == 'A':
            self.modifyVectors(move_x=1)

        #Walk right
        elif e.char == 'd' or e.char == 'D':
            self.modifyVectors(move_x=-1)

    def keyRelease(self, e):
        print (e.char, 'KeyRelease')

    def updateObjects(self):
        pass

    def packObjects(self):
        self.game_canvas.pack(fill="both", expand=True)

    def modifyVectors(self, diff_x=0, diff_y=0, move_x=0, move_y=0, move_z=0):
        screen_vectors = [self.screen_x_vector, self.screen_y_vector, self.camera_vector]

        #Start with screen_vectors
        for v in screen_vectors:
            self.modifySingleVector(v=v, diff_x=diff_x, diff_y=diff_y, move_x=move_x, move_y=move_y, move_z=move_z,screen_vectors=screen_vectors)

        #Then on to all other vectors
        for v in self.all_vectors:
            if v not in screen_vectors:
                self.modifySingleVector(v=v, diff_x=diff_x, diff_y=diff_y, move_x=move_x, move_y=move_y, move_z=move_z, screen_vectors=screen_vectors)


    def modifySingleVector(self, v=Vector([0,0,0], [0,0,0]), diff_x=0, diff_y=0, move_x=0, move_y=0, move_z=0, screen_vectors=[]):
        # Rotate Vector according to the current screen_x/y axis
        if diff_x != 0:
            v.rotateAroundAnotherVector(axis_vector=self.screen_y_vector, angle_of_rotation=diff_x)
        if diff_y != 0:
            v.rotateAroundAnotherVector(axis_vector=self.screen_x_vector, angle_of_rotation=diff_y)

        if v not in screen_vectors:
            #If objects are moving
            if move_x != 0:
                v.start_point += self.screen_x_vector.vector * move_x
                v.end_point += self.screen_x_vector.vector * move_x

            if move_y != 0:
                v.start_point += self.screen_y_vector.vector * move_y
                v.end_point += self.screen_y_vector.vector * move_y

            #Create a 2d of a vector in a 3d space

            #Set start point and end point Vectors
            start_point_vector = Vector(end_point=v.start_point)
            end_point_vector = Vector(end_point=v.end_point)

            #Get 2d coordinates of the start and the end of the 2d vector on that plane
            v.screen_start_point = start_point_vector.get2dCoordinates(self.screen_x_vector, self.screen_y_vector)
            v.screen_end_point = end_point_vector.get2dCoordinates(self.screen_x_vector, self.screen_y_vector)

            scale_x = self.x_axis_scale
            scale_y = self.y_axis_scale
            root_point_x = self.root_point[0]
            root_point_y = self.root_point[1]
            x1 = v.screen_start_point [0]
            y1 = v.screen_start_point[1]
            x2 = v.screen_end_point[0]
            y2 = v.screen_end_point[1]
            self.game_canvas.coords(v.canvas_object,
                    #X1, Y1
                    root_point_x - x1 * scale_x, root_point_y - y1 * scale_y,

                    #X2, Y2
                    root_point_x - x2 * scale_x, root_point_y - y2 * scale_y
                                    )


    def generateVectors(self):
        for v in Vector.all_vectors:
            if v.display_on_screen == True:
                scale_x = self.x_axis_scale
                scale_y = self.y_axis_scale
                root_point_x = self.root_point[0]
                root_point_y = self.root_point[1]

                x1 = v.screen_start_point[0]
                y1 = v.screen_start_point[1]
                x2 = v.screen_end_point[0]
                y2 = v.screen_end_point[1]
                #If the vector on this plane equals 0 create a little line
                if (x2 != x1 or y2 != y2):
                    v.canvas_object = self.game_canvas.create_line(
                        # X1, Y1
                        root_point_x - x1 * scale_x, root_point_y - y1 * scale_y,

                        # X2, Y2
                        root_point_x - x2 * scale_x, root_point_y - y2 * scale_y,

                        fill=v.color
                    )

                else:
                    v.canvas_object = self.game_canvas.create_line(0, 0, 1, 1, fill=v.color)

                self.all_vectors.append(v)
