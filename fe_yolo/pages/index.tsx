import Head from 'next/head'
import {BASE_URL} from "../const"
import axios from "axios";
import {useEffect, useState} from "react";
import _ from "lodash";

export default function Home() {
  const [data, setData] = useState();
  const [active, setActive] = useState(-1);

  async function getData() {
    const resp = await axios.get(`${BASE_URL}/data`, {
      headers: {
        'Content-Type': "application/json"
      }
    })
    if (resp.status === 200) {
      setData(resp.data);
    }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      getData();
    }, 1000)
    return () => {
      clearInterval(interval);
    }
  }, [])

  return (
    <div className="flex flex-col items-center min-h-screen py-2">
      <Head>
        <title>Multi-Camera Object Detection, Tracking, and Counting</title>
        <link rel="icon" href="/favicon.ico"/>
      </Head>

      <div className="text-2xl font-semibold my-6">Multi-Camera Object Detection, Tracking, and Counting</div>

      <div className="max-w-screen-2xl w-full flex">
        <div className="flex flex-col">
          <div className="w-full flex flex-col">
            <div className="flex w-full mb-2">
              <img src={`${BASE_URL}/video_feed/camera/0`} className="center img-container mr-2"/>
              <img src={`${BASE_URL}/video_feed/yolo/0`}
                   className={`center img-container ml-2 ${_.get(data, 'yolo0') >= 1 && 'border-4 border-red-400'}`}
                   onClick={() => setActive(0)}
              />
            </div>
          </div>
          <div className="w-full flex flex-col mb-2">
            <div className="flex w-full">
              <img src={`${BASE_URL}/video_feed/camera/1`} className="center img-container mr-2"/>
              <img src={`${BASE_URL}/video_feed/yolo/1`}
                   className={`center img-container ml-2 ${_.get(data, 'yolo1') >= 1 && 'border-4 border-red-400'}`}
                   onClick={() => setActive(1)}
              />
            </div>
          </div>
          <div className="flex flex-col mb-2">
            <div className="flex">
              <img src={`${BASE_URL}/video_feed/camera/2`} className="center img-container mr-2"/>
              <img src={`${BASE_URL}/video_feed/yolo/2`}
                   className={`center img-container ml-2 ${_.get(data, 'yolo2') >= 1 && 'border-4 border-red-400'}`}
                   onClick={() => setActive(2)}
              />
            </div>
          </div>
        </div>
        <div className="w-80 flex flex-col items-center text-lg font-semibold">
          <div className={`${_.get(data, 'yolo0') >= 1 && 'text-red-400'}`}>Camera 1: {_.get(data, 'yolo0') || 0}</div>
          <div className={`${_.get(data, 'yolo1') >= 1 && 'text-red-400'}`}>Camera 2: {_.get(data, 'yolo1') || 0}</div>
          <div className={`${_.get(data, 'yolo2') >= 1 && 'text-red-400'}`}>Camera 3: {_.get(data, 'yolo2') || 0}</div>
        </div>
      </div>
      <div className={`fixed w-screen h-screen top-0 left-0 ${active > -1 ? 'flex' : 'hidden'}`} onClick={() => setActive(-1)}>
        <img src={`${BASE_URL}/video_feed/yolo/${active}`} className={`center ml-2 img-zoom ${_.get(data, `yolo${active}`) >= 1 && 'border-4 border-red-400'}`}/>
      </div>
    </div>
  )
}
