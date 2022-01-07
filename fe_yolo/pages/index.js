import Head from 'next/head'
import {BASE_URL} from "/const"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <Head>
        <title>Multi-Camera Object Detection, Tracking, and Counting</title>
        <link rel="icon" href="/favicon.ico"/>
      </Head>

      <div className="text-xl font-semibold">Multi-Camera Object Detection, Tracking, and Counting</div>
      <div className="flex flex-col gap-3 max-w-screen-xl w-full">

        <div className="flex">
          <div className="flex-1 mr-2">
            <div className="text-center">Camera stream 1</div>
            <img src={`${BASE_URL}/video_feed/camera/0`} alt="Camera stream 1" className="img-container"/>
          </div>
          <div className="flex-1 ml-2">
            <div className="text-center">YOLO stream 1</div>
            <img src={`${BASE_URL}/video_feed/yolo/0`} alt="YOLO Stream 1" className="img-container"/>
          </div>
        </div>

        <div className="flex">
          <div className="flex-1 mr-2">
            <div className="text-center">Camera stream 2</div>
            <img src={`${BASE_URL}/video_feed/camera/1`} alt="Camera stream 2" className="img-container"/>
          </div>
          <div className="flex-1 ml-2">
            <div className="text-center">YOLO stream 2</div>
            <img src={`${BASE_URL}/video_feed/yolo/1`} alt="YOLO Stream 2" className="img-container"/>
          </div>
        </div>
      </div>
    </div>
  )
}

export async function getServerSideProps(context) {
  return {
    props: {},
  }
}
