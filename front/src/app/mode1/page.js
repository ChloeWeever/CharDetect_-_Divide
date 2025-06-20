"use client";
import Image from "next/image";
import React, {useState} from "react";
import {FileUpload} from "@/components/ui/file-upload";
import {Checkbox, FormControlLabel, FormGroup, TextField} from "@mui/material";
import Link from "next/link";
import axios from 'axios';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';

export default function ImageEditor() {
    const [files, setFiles] = useState([]);
    const [imageSrc, setImageSrc] = useState(null);
    const [width, setWidth] = useState(500);
    const [height, setHeight] = useState(500);
    const [processedImages, setProcessedImages] = useState([]);
    const [selectedStyle, setSelectedStyle] = useState("no"); // 新增：跟踪选中项
    const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false); // 新增：控制弹窗显示状态
    const [progress, setProgress] = useState(0); // 进度条状态

    const startLoading = () => {
        let currentProgress = 0;

        const simulateProgress = () => {
            // 非线性公式：指数增长，接近目标值时减速
            currentProgress += (99 - currentProgress) * 0.1; // 趋近于90%
            setProgress(Math.min(currentProgress, 99));

            if (currentProgress < 98) {
                setTimeout(simulateProgress, 100); // 控制更新频率
            }
        };

        simulateProgress();
    };


    const handleFileUpload = (files) => {
        const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
        if (imageFiles.length > 0) {
            setFiles([imageFiles[0]]);
            setImageSrc(URL.createObjectURL(imageFiles[0]));
        } else {
            alert("请上传有效的图片文件");
        }
    };

    // 提取按钮的回调函数
    const handleExtract = () => {
        if (!imageSrc || files.length === 0) {
            alert("请先上传图片");
            return;
        }

        startLoading();
        const _width = width;
        const _height = height;
        const selectedFile = files[0]; // 获取用户上传的文件

        // 创建 FormData 对象并添加必要的字段
        const formData = new FormData();
        formData.append('image', selectedFile); // 添加图片文件
        formData.append('width', _width);
        formData.append('height', _height);
        formData.append('style', selectedStyle);

        // 发起请求
        axios.post('http://127.0.0.1:5000/api/detect', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(response => {
            console.log('请求成功:', response.data)
            setProgress(100);
            if (response.data && response.data.processed_images && response.data.processed_images.length > 0) {
                // 弹窗显示预览图
                setIsPreviewModalOpen(true); // 打开弹窗
                setProcessedImages(response.data.processed_images);
            } else {
                alert('未找到处理后的图片数据');
            }
        }).catch(error => {
            console.error('请求失败:', error);
            alert('处理图片时发生错误');
        });
    };

    const handleDownloadAll = () => {
        processedImages.forEach(src => {
            const link = document.createElement("a");
            link.href = src;
            link.download = src.split("/").pop(); // 使用文件名下载
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    };

    // 新增：关闭弹窗的函数
    const handleCloseModal = () => {
        setIsPreviewModalOpen(false);
        setProcessedImages([]); // 清空处理结果
    };

    // 新增：确认使用的函数
    const handleConfirm = () => {
        setIsPreviewModalOpen(false); // 关闭弹窗
    };

    return (
        <div className="flex h-screen">
            {/* 左侧 - 图片区域 */}
            <div className="w-2/3 flex flex-col items-center justify-center border-r border-gray-300 p-4">
                <div
                    className="w-full max-w-4xl mx-auto min-h-96 border border-dashed bg-white dark:bg-black border-neutral-200 dark:border-neutral-800 rounded-lg">
                    {imageSrc ? (
                        <div className="relative w-full h-full">
                            <Image
                                src={imageSrc}
                                alt="上传的图片"
                                layout="fill"
                                objectFit="contain"
                                className="rounded-lg"
                            />
                        </div>
                    ) : (
                        <FileUpload onChange={handleFileUpload}/>
                    )}
                </div>
            </div>

            {/* 右侧 - 操作区域 */}
            <div className="w-1/3 flex flex-col items-start justify-start p-6 gap-4 bg-gray-50">
                <Link href="/"
                      className="absolute top-4 right-4 inline-flex h-10 px-4 overflow-hidden rounded-full bg-blue-500 text-white justify-center items-center text-sm font-medium">
                    笔画分割↗
                </Link>
                <h2 className="text-5xl font-semibold">文字提取</h2>
                <FormControl>
                    <FormLabel id="demo-row-radio-buttons-group-label">后处理风格</FormLabel>
                    <RadioGroup
                        row
                        aria-labelledby="demo-row-radio-buttons-group-label"
                        name="row-radio-buttons-group"
                        value={selectedStyle} // 绑定当前选中值
                        onChange={(e) => setSelectedStyle(e.target.value)} // 更新状态
                    >
                        <FormControlLabel value="no" control={<Radio/>} label="无"/>
                        <FormControlLabel value="enhance" control={<Radio/>} label="增强"/>
                        <FormControlLabel value="watercolor" control={<Radio/>} label="水彩"/>
                        <FormControlLabel value="pencil_sketch" control={<Radio/>} label="素描"/>
                        <FormControlLabel value="bit" control={<Radio/>} label="二值化"/>
                    </RadioGroup>
                </FormControl>

                {/* 添加宽度和高度输入框 */}
                <p className="font-medium">输出大小</p>
                <div className="flex gap-4">
                    <TextField
                        label="宽度"
                        type="number"
                        value={width}
                        onChange={(e) => setWidth(Number(e.target.value))}
                        variant="outlined"
                        size="small"
                        fullWidth
                    />
                    <TextField
                        label="高度"
                        type="number"
                        value={height}
                        onChange={(e) => setHeight(Number(e.target.value))}
                        variant="outlined"
                        size="small"
                        fullWidth
                    />
                </div>

                {progress > 0 && (
                    <div className="w-full mt-4 bg-gray-200 rounded-full h-2">
                        <div
                            className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-out"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                )}

                {processedImages.length > 0 ? (
                    <div className="mt-4 w-full">
                        <h3 className="font-medium mb-2">处理结果：</h3>
                        <button
                            onClick={handleDownloadAll}
                            className="mt-4 w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 transition-colors"
                        >
                            一键下载全部
                        </button>
                        <div className="mt-4 max-h-96 overflow-y-auto pr-2">
                            <div className="grid grid-cols-2 gap-2">
                                {processedImages.slice(1).map((src, index) => (
                                    <div key={index} className="relative aspect-square">
                                        <Image
                                            src={src}
                                            alt={`处理结果 ${index}`}
                                            layout="fill"
                                            objectFit="cover"
                                            className="rounded-md"
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (<button onClick={handleExtract}
                             className="relative inline-flex h-12 w-full overflow-hidden rounded-full p-[1px] focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50">
                    <span
                        className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#E2CBFF_0%,#393BB2_50%,#E2CBFF_100%)]"/>
                    <span
                        className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-slate-950 px-3 py-1 text-sm font-medium text-white backdrop-blur-3xl">
                        提取!
                    </span>
                </button>)}

            </div>

            {/* 新增：自定义弹窗 */}
            {isPreviewModalOpen && (
                <div className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg w-96">
                        <h3 className="text-xl font-semibold mb-4">预览图</h3>
                        {/* 修改：显示所有处理后的图片 */}
                        <div className="grid grid-cols-2 gap-2">
                            <img
                                src={processedImages[0]}
                                alt={`预览图`}
                                className="w-64 object-contain mb-4"
                            />
                        </div>
                        <div className="flex justify-end gap-4">
                            <button
                                onClick={handleCloseModal}
                                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                            >
                                取消
                            </button>
                            <button
                                onClick={handleConfirm}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                确认
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}