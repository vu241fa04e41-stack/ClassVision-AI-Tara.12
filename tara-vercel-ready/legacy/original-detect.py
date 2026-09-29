from ultralytics import YOLO


model = YOLO("yolo11n.pt")



def detect_objects(frame):


    results = model(frame)



    persons = 0

    objects = []



    for result in results:


        for box in result.boxes:


            cls = int(box.cls[0])

            name = model.names[cls]


            objects.append(name)



            # Person class
            if name == "person":

                persons += 1



    return {

        "persons": persons,

        "objects": objects,

        "result": results[0].plot()

    }