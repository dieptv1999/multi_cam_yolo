#install package 

pip3 install -r requirements.txt
#Để chạy project thì cần có multicam

##Để chạy giả lập từ video có thể chạy folder video_streamer
> cd ./video_streamer
> python3 ./video_streamer -p 5555 -p 5566 -v test3.mp4 -v test5.mp4
với -p là port để xuất stream
và -v là đường dẫn đến file video 
-> ta đã có 2 camera để test ứng dụng
 Ngoài ra có thể chạy trực tiếp từ link rtsp hoặc camera máy tính với các file camera_client_*.py
 với mỗi file là chạy stream để đọc frame từ link rtsp hoặc camera để public ra connect_to=tcp://127.0.0.1:<port>
 
 ##Chạy object_detecting
 cd ./object_detecting
 python3 app.py -c person
 
 với -c là flag class (person), có thể chạy multi class: -c person -c car
 
 #Để chạy front end -> đọc readme trong folder fe_yolo
