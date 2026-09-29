from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import cv2


app = Flask(__name__)


# YOLO Model
model = YOLO("yolo11n.pt")



# 25 Camera Setup

cameras = {}

for i in range(25):

    cameras[i+1] = cv2.VideoCapture(i)



# YOLO Detection + Video Stream

def generate(camera_id):

    camera = cameras[camera_id]


    while True:

        success, frame = camera.read()


        if not success:
            continue



        # YOLO Detection

        results = model(frame)


        student_count = 0


        for result in results:

            for box in result.boxes:


                cls = int(box.cls[0])


                # COCO class 0 = person

                if cls == 0:

                    student_count += 1




        # Draw boxes

        frame = results[0].plot()



        # Add student count text

        cv2.putText(

            frame,

            f"Students: {student_count}",

            (20,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (0,255,0),

            2

        )



        # Convert image


        ret, buffer = cv2.imencode(

            ".jpg",

            frame

        )


        frame = buffer.tobytes()



        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame +

            b"\r\n"

        )





# Main Dashboard

@app.route("/")

def dashboard():

    return render_template(
        "dashboard.html"
    )





# Camera Stream Route

@app.route("/video/<int:id>")

def video(id):


    if id not in cameras:

        return "Camera Not Found"



    return Response(

        generate(id),

        mimetype=

        "multipart/x-mixed-replace; boundary=frame"

    )





# AI Analytics API

@app.route("/analytics")

def analytics():


    data = {


        "total_classes":25,


        "total_students":850,


        "attendance":92,


        "cameras":25


    }


    return jsonify(data)





# Run Server

if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )