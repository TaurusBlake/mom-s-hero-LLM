#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Speech Service 語音處理模組
支援 Line Bot 語音訊息轉文字功能
"""

import os
import logging
import tempfile
from typing import Optional
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

class SpeechProcessor:
    """Azure Speech Service 語音處理器"""
    
    def __init__(self, azure_key: str, azure_region: str):
        """
        初始化語音處理器
        
        Args:
            azure_key: Azure Speech Service 金鑰
            azure_region: Azure Speech Service 區域
        """
        self.azure_key = azure_key
        self.azure_region = azure_region
        
        # 設定日誌
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Azure Speech 配置
        self.speech_config = speechsdk.SpeechConfig(
            subscription=azure_key, 
            region=azure_region
        )
        
        # 設定語言為繁體中文
        self.speech_config.speech_recognition_language = "zh-TW"
        
        self.logger.info("Azure Speech Service 初始化成功")
    
    def convert_audio_format(self, input_file: str, output_file: str) -> bool:
        """
        轉換音訊格式（AAC/M4A → WAV）
        
        Args:
            input_file: 輸入檔案路徑
            output_file: 輸出檔案路徑
            
        Returns:
            轉換是否成功
        """
        try:
            # 載入音訊檔案
            audio = AudioSegment.from_file(input_file)
            
            # 轉換為 WAV 格式
            audio.export(output_file, format="wav")
            
            self.logger.info(f"音訊格式轉換成功: {input_file} → {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"音訊格式轉換失敗: {e}")
            return False
    
    def speech_to_text(self, audio_file: str) -> Optional[str]:
        """
        使用 Azure Speech Service 將語音轉為文字
        
        Args:
            audio_file: 音訊檔案路徑（WAV 格式）
            
        Returns:
            轉換後的文字，失敗則返回 None
        """
        try:
            # 建立音訊配置
            audio_config = speechsdk.AudioConfig(filename=audio_file)
            
            # 建立語音識別器
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            # 執行語音識別
            self.logger.info(f"開始語音識別: {audio_file}")
            result = speech_recognizer.recognize_once_async().get()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                self.logger.info(f"語音識別成功: {text}")
                return text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.logger.warning("語音識別失敗：無法識別語音內容")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                self.logger.error(f"語音識別取消: {cancellation_details.reason}")
                return None
            else:
                self.logger.error(f"語音識別未知錯誤: {result.reason}")
                return None
                
        except Exception as e:
            self.logger.error(f"語音識別過程發生錯誤: {e}")
            return None
    
    def process_line_audio(self, audio_file: str) -> Optional[str]:
        """
        處理 Line Bot 語音檔案
        
        Args:
            audio_file: Line Bot 語音檔案路徑（AAC/M4A 格式）
            
        Returns:
            轉換後的文字，失敗則返回 None
        """
        try:
            # 建立暫存 WAV 檔案
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # 轉換格式
            if not self.convert_audio_format(audio_file, temp_wav_path):
                return None
            
            # 語音轉文字
            text = self.speech_to_text(temp_wav_path)
            
            # 清理暫存檔案
            try:
                os.remove(temp_wav_path)
            except:
                pass
            
            return text
            
        except Exception as e:
            self.logger.error(f"處理 Line 語音檔案失敗: {e}")
            return None
    
    def get_supported_formats(self) -> list:
        """獲取支援的音訊格式"""
        return ["aac", "m4a", "mp3", "wav", "ogg"]
    
    def get_max_duration(self) -> int:
        """獲取最大支援的語音時長（秒）"""
        return 15  # Azure Speech Service RecognizeOnceAsync 限制

# 全域語音處理器實例
speech_processor = None

def init_speech_processor(azure_key: str, azure_region: str):
    """初始化全域語音處理器"""
    global speech_processor
    try:
        speech_processor = SpeechProcessor(azure_key, azure_region)
        logging.info("語音處理器初始化成功")
    except Exception as e:
        logging.error(f"語音處理器初始化失敗: {e}")
        speech_processor = None

def get_speech_processor() -> Optional[SpeechProcessor]:
    """獲取全域語音處理器實例"""
    return speech_processor 