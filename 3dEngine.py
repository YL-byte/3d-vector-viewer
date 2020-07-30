from gui import App, Vector
#import read_stl
#Initialize App
app = App(width=1000, height=700, x_axis_scale=200, y_axis_scale=200, zoom=100, drag_scale=1)

#Triangle XY
v1 = Vector([0,0,0],[1,0,0])
v2 = Vector([0,0,0],[0,1,0])
v3 = Vector([0,1,0],[1,0,0])

#Square XY
v4 = Vector([0,0,0],[0,0,1])
z5 = Vector([0,1,0],[0,1,1])
v6 = Vector([0,0,1],[0,1,1])

#Triangle XY
v7 = Vector([0,0,1],[1,0,1])
v8 = Vector([0,0,1],[0,1,1])
v9 = Vector([0,1,1],[1,0,1])

#Close Square
v10 = Vector([1,0,0],[1,0,1])

app.generateVectors()
app.packObjects()
app.modifyVectors()
app.mainloop()