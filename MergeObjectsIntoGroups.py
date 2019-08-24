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
    for o in selobj:
        if group.name == o.name:
            #make a list of all objects in group
            print ("starting " + group.name)
            objInGroup = []
            for obj in group.objects:
                if obj.type == "MESH":
                    objInGroup.append(obj)

            #find object corresponding to group (object to replace has to be named the same as group)
            for obj in bpy.data.objects:
                if obj.name == group.name:
                    print("found object for "+ obj.name)
                    oldObj = obj
                    oldObjmatrix = obj.matrix_world
                    objName = obj.name
                
            #go though list of objects and..
            objInGroupNew = []
            for obj in objInGroup:
                print ("obj name = " + obj.name) 
                if obj.name != objName:
                    objData = obj.data.copy()         #get data from object

                    ob = bpy.data.objects.new("MergeMe"+ obj.name[-4:], objData)   #add that data to a new object
                    ob.matrix_world = obj.matrix_world              #in the same place as the old one
                                         
                    scn.objects.link(ob)        #add to scene
                    objInGroupNew.append(ob)    #add to list of NEW objects
                    copyModifier(obj,ob)
                    
                    scn.update()

            #rename old object ready for delete
            oldObj.name = "DELETEME"

            # select all new objects
            for obj in bpy.data.objects:
                for objG in objInGroupNew:
                    if obj.name in objG.name:
                        obj.select = True 
                        bpy.context.scene.objects.active = obj
                        break
                    obj.select = False
                    
            #apply modifiers(have been copied)
            bpy.ops.object.convert(target='MESH')

            #apply scale and transform info
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            #make a new object to merge all new objects into, add to scene and set transform based on old one
            me = bpy.data.meshes.new(group.name)
            ob = bpy.data.objects.new(group.name, me)
            scn.objects.link(ob)
            ob.matrix_world = oldObjmatrix

            #select this new object
            ob.select = True
            bpy.context.scene.objects.active = ob  #has to be active so join works

            #merge all new objects into one
            bpy.ops.object.join()

            #copy layer info and modifiers from old models to new one
            ob.layers = oldObj.layers
            oldObj.select = True
            bpy.context.scene.objects.active = oldObj
            bpy.ops.object.make_links_data(type="MODIFIERS")

            #remove old object
            scn.objects.unlink(oldObj)
            oldObj.user_clear()
            scn.update()

            print("finished " + group.name)