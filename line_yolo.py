import warnings
warnings.filterwarnings("ignore")

from ultralytics import YOLO
import cv2
import math
import time
import numpy as np
import threading

# LINE Notify configuration
url = 'https://notify-api.line.me/api/notify'
token = 'XV2Jj6g6RJ2DSxlKGlvVgM9pmFcekVspSpERd1TxPP5'
headers = { 
    'Authorization': 'Bearer ' + token
}
dangerous_message = {
    'message': '\n情緒狀態:危險駕駛!!',
    'stickerPackageId': '11537',
    'stickerId': '52002749'
}
safe_message = {
    'message': '\n情緒狀態:安全駕駛',
    'stickerPackageId': '6325',
    'stickerId': '10979904'
}
tired_message = {
    'message': '\n情緒狀態:危險駕駛!!\n駕駛是否為疲勞:是',
    'stickerPackageId': '11538',
    'stickerId': '51626531'
}
nottired_message = {
    'message': '\n情緒狀態:危險駕駛!!\n駕駛是否為疲勞:否',
}

def send_line_notify(S, D, T):
    print("/n傳送中")
    lock.acquire()         # 鎖定
    if S > D:
        if T > 3:
            requests.post(url, headers=headers, data=tired_message)
        else:
            requests.post(url, headers=headers, data=nottired_message)
    else:
        requests.post(url, headers=headers, data=safe_message)
    lock.release()

def initialize_system():
    # start webcam
    cap = cv2.VideoCapture(0)

    # Load models
    model = YOLO("model/2modelmerge_300.pt")

    # Object classes
    classNames = ['angry', 'happy', 'neutral', 'sad', 'surprised', 'tired']

    frame_times = [] # frame count

    # score calculate initialize
    transfer = {
        'happy': 'safe',
        'tired': 'tired',
        'sad': 'danger',
        'angry': 'danger',
        'surprised': 'danger',
        'neutral': 'safe'
    }
    SIZE = 15
    EmotionDetect = np.empty(SIZE, dtype='U15') # for emotion detection
    index = 0
    count_time = 0
    index_count = 0
    data = None

    return cap,model,classNames,frame_times,SIZE,transfer,EmotionDetect,index,count_time,index_count,data


def FirstModel(model , GrayFrame):
    max_confidence = 0
    max_confidence_box = None

    results = model(GrayFrame, stream=True)
    # Find the box with the highest confidence
    for r in results:
        boxes = r.boxes
        for box in boxes:
            confidence = box.conf[0]
            if confidence > max_confidence:
                max_confidence = confidence
                max_confidence_box = box
        break
    return max_confidence,max_confidence_box

def frame(frame_times):
    # Keep only the last 8 frame times

    if len(frame_times) > 8:
        frame_times.pop(0)

    # Calculate FPS based on the average time difference between frames
    if len(frame_times) > 1:
        fps = len(frame_times) / (frame_times[-1] - frame_times[0])
    else:
        fps = 0

    return fps

def output_result(count_S,count_D,count_T):

    if count_S == 0 and count_D == 0:
       print("無偵測到駕駛員的情緒反應")

    elif count_S > count_D:
        print("情緒狀態: 安全駕駛!!")

    elif count_S < count_D:
        print("情緒狀態: 危險駕駛!!")
    else:
        print("情緒狀態:中性，建議保持警惕")

    if count_T > 7 :
        print("駕駛是否為疲勞: 是")
    else:
        print("駕駛是否為疲勞: 否")


def main():
    cap,model,classNames,frame_times,SIZE,transfer,EmotionDetect,index,count_time,index_count,data = initialize_system()

    if not cap.isOpened():
        print("Web Camera not detected")
        exit()

    while True:
        success, img = cap.read()

        if not success:
            print("failed to capture image")
            break
        count_time +=1

        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        end_time = time.time()
        frame_times.append(end_time)

        # model face emotion detection
        gray_frame_3channel = cv2.merge([gray_frame, gray_frame, gray_frame]) 

        max_confidence,max_confidence_box = FirstModel(model , gray_frame_3channel)

        if max_confidence_box is not None and max_confidence > 0.6:
            x1, y1, x2, y2 =  max_confidence_box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # put box in cam
            cls = int(max_confidence_box.cls[0])

            if classNames[cls] in ["angry","sad","surprised","tired"]:
                cv2.rectangle(gray_frame_3channel, (x1, y1), (x2, y2), (0, 255, 0), 3)

            data = classNames[cls]

            # object details
            cv2.putText(gray_frame_3channel , classNames[cls], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,0, 255), 3)

        else: # confidence < 0.6
            cv2.rectangle(gray_frame_3channel , (0, 0), (0, 0), (0, 0, 0))
            data = None

        # driver emotion evaluation
        if count_time > 7:
            SD = transfer.get(data)

            if SD is not None:
                EmotionDetect[index] = SD
                index = (index + 1) % SIZE
                index_count+=1

            else:
                EmotionDetect[index] = " "
                index = (index + 1) % SIZE
                index_count+=1

            print("list1内容:")
            for item in EmotionDetect:
                print(item)

            # 初始化
            count_S = 0
            count_D = 0
            count_T = 0
            const_T = False

           # 計算list1中的SD個數
            for item in EmotionDetect:
                 # detect safe
                if item == 'safe':
                    count_S += 1
                    const_T = False # reset if not detect tired

                # detect danger
                elif item == 'danger':
                    count_D += 1
                    const_T = False # reset  if not detect tired

                 # detect tired
                elif item == 'tired' :
                    count_D += 1

                    if const_T:
                        count_T += 1
                    else:
                        count_T = 1     # 開始計數
                        const_T = True  # 設置為連續 tired
                else:
                    const_T = False  # reset

            print(f"幾次安全:  {count_S}")
            print(f"幾次危險:  {count_D}\n")

            if index_count == SIZE:
                output_result(count_S,count_D,count_T)
                index_count = 0 # 重新計數
                threading.Thread(target=send_line_notify, args=(count_S, count_D, count_T)).start()
                print("/傳送完成")

            count_time = 0

        # fps calculate
        fps = frame(frame_times)
        fps_text = "FPS: {:.1f}" .format(fps) # Display FPS on the frame

        # ouput all detection result fps、face_emotion
        cv2.putText(gray_frame_3channel, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255 , 0, 255), 3)
        cv2.imshow('predict', gray_frame_3channel)

        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()