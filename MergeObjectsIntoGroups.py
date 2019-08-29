import bpy

def copyModifier(source, target):
    active_object = source
    obj = target

    for mSrc in active_object.modifiers:
        mDst = obj.modifiers.get(mSrc.name, None)
        if not mDst:
            mDst = obj.modifiers.new(mSrc.name, mSrc.type)

        # collect names of writable properties
        properties = [p.identifier for p in mSrc.bl_rna.properties
                      if not p.is_readonly]

        # copy those properties
        for prop in properties:
            setattr(mDst, prop, getattr(mSrc, prop))

print ("-----------------------------")
scn = bpy.context.scene
selobj = bpy.context.selected_objects
groups = []

#check seleted objects have groups
for group in bpy.data.groups:
    for selectedObject in selobj:
        if group.name == selectedObject.name:
            print ("starting " + group.name)

            #make a list of all objects in group
            objectsInGroup = []
            for obj in group.objects:
                if obj.type == "MESH":
                    objectsInGroup.append(obj)

            #find object named same as group to be replaced
            try: 
                objectToBeReplaced = bpy.data.objects[group.name]

                newObjectsList = []
                #go though list of objects in group and..
                for objectInGroup in objectsInGroup:
                    print ("obj name = " + objectInGroup.name) 
                    if objectInGroup.name == objectToBeReplaced.name:
                        continue

                    objData = objectInGroup.data.copy()         #get data from object

                    obj = bpy.data.objects.new("MergeMe"+ objectInGroup.name[-4:], objData)   #add that data to a new object
                    obj.matrix_world = objectInGroup.matrix_world              #in the same place as the old one
                                        
                    scn.objects.link(obj)        #add to scene
                    newObjectsList.append(obj)    #add to list of NEW objects

                    for vertexGroup in objectInGroup.vertex_groups:  
                        obj.vertex_groups.new(vertexGroup.name)
                    copyModifier(objectInGroup,obj)
                    
                    scn.update()

                #rename old object ready for delete
                objectToBeReplaced.name = "DELETEME"

                # select all new objects
                for obj in bpy.data.objects:
                    for objG in newObjectsList:
                        if obj.name in objG.name:
                            obj.select = True 
                            bpy.context.scene.objects.active = obj
                            break
                        obj.select = False
                        
                #apply modifiers(have been copied)
                bpy.ops.object.convert(target='MESH')
                print("a")
                #apply scale and transform info
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                #make a new object to merge all new objects into, add to scene and set transform based on old one
                me = bpy.data.meshes.new(group.name)
                print("b")
                obj = bpy.data.objects.new(group.name, me)
                print("bb")
                scn.objects.link(obj)
                print("cc")
                obj.matrix_world = objectToBeReplaced.matrix_world
                print("d")
                #select this new object
                obj.select = True
                bpy.context.scene.objects.active = obj  #has to be active so join works
                print("d")
                #merge all new objects into one
                bpy.ops.object.join()
                print("e")
                #copy layer info and modifiers from old models to new one
                obj.layers = objectToBeReplaced.layers
                objectToBeReplaced.select = True
                print("f")
                bpy.context.scene.objects.active = objectToBeReplaced
                bpy.ops.object.make_links_data(type="MODIFIERS")
                print("c")
                #remove old object
                scn.objects.unlink(objectToBeReplaced)
                objectToBeReplaced.user_clear()
                scn.update()

                print("finished " + group.name)

            except:
                print ("no object found for group " + group.name)
                
    