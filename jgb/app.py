from flask import Flask, request, jsonify, Response
from flask import stream_with_context, render_template
from dotenv import load_dotenv
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
import mysql.connector
import boto3
import os
import urllib.request
from flask import send_file
from init import setting
from videocode import video_func
from DBcode import DB_func

projectlocal = os.path.dirname(__file__)

app = Flask(__name__, static_folder=projectlocal + "/videostreaming/")
api = Api(app)  # Flask 객체에 Api 객체 등록

conn = DB_func.rds_connect()  # 이게 된다고?

s3c, s3r, strlocal, bucket, bucket_name = video_func.video_init()


@app.route("/videowatch")
def index():
    # 로컬 동영상 경로 설정
    video_path = "streamingvideo.mp4"
    print(video_path)
    # iFrame으로 동영상 재생
    return render_template("iframe.html", video_path=video_path)


@api.route("/sensor/insert", methods=["POST"])
class sensorinsert(Resource):
    def post(self):
        try:
            strdate, straccel, strbreak, intspeed = DB_func.sensor_insert(
                request.get_json(), conn
            )
            return {
                "inserted successfully!": "%s, %s, %s, %d"
                % (strdate, straccel, strbreak, intspeed)
            }
        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"


@api.route("/sensor/select")
class sensorselect(Resource):
    def get(self):
        try:
            data = DB_func.sensor_select(conn)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/select")
class normalselect(Resource):
    def get(self):
        try:
            data = DB_func.normal_select(conn)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/crashvideo/select")
class crashselect(Resource):
    def get(self):
        try:
            data = DB_func.crash_select(conn)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/watch/<strvideodate>")
class watchnormal(Resource):
    def get(self, strvideodate):
        try:
            # data = request.get_json()
            # strvideodate = data["strvideodate"]
            # strvideodate = request.form.get("strvideodate")
            # if strvideodate is None:
            #     return "input data : None "
            print(strvideodate)
            DB_func.normal_watch(conn, strvideodate)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        setting.folder_make("down", "", None, None)

        video_func.normal_download(bucket, strvideodate)

        video_func.incord()

        return "http://43.201.154.195:5000/videowatch"


@api.route("/crashvideo/watch/<strvideodate>")
class watchcrash(Resource):
    def get(self, strvideodate):
        try:
            # data = request.get_json()
            # strvideodate = data["strvideodate"]
            # strvideodate = request.form.get("strvideodate")
            # if strvideodate is None:
            #     return "input data : None "
            print(strvideodate)
            DB_func.crash_watch(conn, strvideodate)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        setting.folder_make("down", "", None, None)

        video_func.crash_download(bucket, strvideodate)

        video_func.incord()

        return "http://43.201.154.195:5000/videowatch"


@api.route("/normalvideo/upload")
class normalvideo(Resource):
    def post(self):
        try:
            file = request.files["normalvideo"]  # 'file'은 업로드된 파일의 key 값입니다.

            setting.folder_make("up", "normal", file, bucket)

            DB_func.normal_upload_insert(conn, file)

            # # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to video upload: {error}")
            return f"Failed to video upload: {error}"


@api.route("/crashvideo/upload")
class crashvideo(Resource):
    def post(self):
        try:
            # 업로드된 파일 ec2에 저장
            file = request.files["crashvideo"]  # 'file'은 업로드된 파일의 key 값입니다.

            setting.folder_make("up", "crash", file, bucket)

            DB_func.crash_upload_insert(conn, file)

            # # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to video upload: {error}")
            return f"Failed to video upload: {error}"


@api.route("/normalvideo/download/<strvideodate>")
class videodown(Resource):
    def get(self, strvideodate):
        url = video_func.generate_presigned_url(
            "normal", bucket_name, "normalvideo/" + strvideodate, strvideodate, s3c
        )
        file_name = strvideodate
        # send_file 함수로 파일 다운로드를 위한 Response 객체 생성
        response = send_file(urllib.request.urlopen(url), mimetype="video/mp4")
        # 파일 다운로드를 위한 헤더 설정
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

        return response


@api.route("/crashvideo/download/<strvideodate>")
class videodown(Resource):
    def get(self, strvideodate):
        url = video_func.generate_presigned_url(
            "crash", bucket_name, "crashvideo/" + strvideodate, strvideodate, s3c
        )
        file_name = strvideodate
        # send_file 함수로 파일 다운로드를 위한 Response 객체 생성
        response = send_file(urllib.request.urlopen(url), mimetype="video/mp4")
        # 파일 다운로드를 위한 헤더 설정
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        
        return response


@api.route("/normalvideo/find", methods=["POST"])  # 검색기능 만들기만해둠
class selectnormal(Resource):
    def post(self):
        try:
            data = DB_func.normal_find(conn, request.get_json())

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


@api.route("/crashvideo/find", methods=["POST"])
class selectnormal(Resource):
    def post(self):
        try:
            data = DB_func.crash_find(conn, request.get_json())

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


# @api.route("/normalvideo/delete/<strvideodate>")  # 영상제거 s3권한이슈로 보류
# class videodel(Resource):
#     def get(self, strvideodate):
#         object = s3r.Object(bucket_name, "normalvideo/" + strvideodate)
#         object.delete()
#         # s3c.delete_object(Bucket=bucket_name, Key="normalvideo/test.mp4")

#         return "video " + strvideodate + " has deleted"


@api.route("/eyes/insert", methods=["POST"])
class eyesinsert(Resource):
    def post(self):
        try:
            strdate, streyesnow = DB_func.eyes_insert(request.get_json(), conn)
            return {"inserted successfully!": "%s, %s" % (strdate, streyesnow)}
        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"


@api.route("/eyes/select")
class eyesselect(Resource):
    def get(self):
        try:
            data = DB_func.eyes_select(conn)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
