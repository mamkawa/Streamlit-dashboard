// OpenMeteo APIのベースURL
const WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast';

// 東京の緯度経度
const TOKYO_LAT = 35.6762;
const TOKYO_LON = 139.6503;

/**
 * 天気情報を取得して Slack に通知する
 */
function notifyWeather() {
  try {
    // 天気情報を取得
    const weatherData = fetchWeatherData();
    
    // Slackメッセージを作成
    const message = createWeatherMessage(weatherData);
    
    // Slackに送信
    postToSlack(message);
    
  } catch (error) {
    console.error('エラーが発生しました:', error);
  }
}

/**
 * OpenMeteo APIから天気データを取得
 */
function fetchWeatherData() {
  const url = `${WEATHER_API_URL}?latitude=${TOKYO_LAT}&longitude=${TOKYO_LON}&hourly=temperature_2m,precipitation_probability,weathercode&timezone=Asia%2FTokyo`;
  const response = UrlFetchApp.fetch(url);
  return JSON.parse(response.getContentText());
}

/**
 * 天気コードを日本語の天気に変換
 */
function getWeatherDescription(code) {
  const weatherCodes = {
    0: '快晴',
    1: '晴れ',
    2: '晴れ時々曇り',
    3: '曇り',
    45: '霧',
    48: '霧氷',
    51: '小雨',
    53: '雨',
    55: '強い雨',
    61: '小雨',
    63: '雨',
    65: '強い雨',
    71: '小雪',
    73: '雪',
    75: '強い雪',
    77: '霧雪',
    80: '小雨',
    81: '雨',
    82: '強い雨',
    85: '小雪',
    86: '雪'
  };
  return weatherCodes[code] || '不明';
}

/**
 * 天気情報からSlackメッセージを作成
 */
function createWeatherMessage(weatherData) {
  const today = new Date();
  const hourly = weatherData.hourly;
  
  // 最高気温と最低気温を計算
  const temperatures = hourly.temperature_2m.slice(0, 24);
  const maxTemp = Math.max(...temperatures);
  const minTemp = Math.min(...temperatures);
  
  // 天気の概況（最も頻出する天気を使用）
  const weatherCodes = hourly.weathercode.slice(0, 24);
  const weatherCount = {};
  let maxCount = 0;
  let mainWeather = '';
  
  weatherCodes.forEach(code => {
    weatherCount[code] = (weatherCount[code] || 0) + 1;
    if (weatherCount[code] > maxCount) {
      maxCount = weatherCount[code];
      mainWeather = getWeatherDescription(code);
    }
  });
  
  // 降水確率の最大値
  const precipProbs = hourly.precipitation_probability.slice(0, 24);
  const maxPrecip = Math.max(...precipProbs);
  
  let message = `*${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日の天気予報*\n\n`;
  message += `天気: ${mainWeather}\n`;
  message += `最高気温: ${maxTemp.toFixed(1)}°C\n`;
  message += `最低気温: ${minTemp.toFixed(1)}°C\n`;
  message += `最大降水確率: ${maxPrecip}%\n`;
  
  return message;
}

/**
 * Slackにメッセージを投稿
 */
function postToSlack(message) {
  const SLACK_WEBHOOK_URL = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_URL');
  if (!SLACK_WEBHOOK_URL) {
    throw new Error('Slack Webhook URLが設定されていません。スクリプトプロパティに"SLACK_WEBHOOK_URL"を設定してください。');
  }

  const payload = {
    "text": message,
    "channel": "#天気通知"
  };
  
  const options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };
  
  UrlFetchApp.fetch(SLACK_WEBHOOK_URL, options);
}

/**
 * 毎日午前6時に実行するトリガーを設定
 */
function setTrigger() {
  ScriptApp.newTrigger('notifyWeather')
    .timeBased()
    .everyDays(1)
    .atHour(6)
    .create();
}