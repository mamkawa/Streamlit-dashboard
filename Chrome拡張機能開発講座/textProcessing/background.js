// コンテキストメニューの作成
chrome.runtime.onInstalled.addListener(() => {
  // 全角・半角変換メニュー
  chrome.contextMenus.create({
    id: "convertToFullWidth",
    title: "全角に変換",
    contexts: ["selection"]
  });
  
  chrome.contextMenus.create({
    id: "convertToHalfWidth",
    title: "半角に変換",
    contexts: ["selection"]
  });

  // 文字数カウントメニュー
  chrome.contextMenus.create({
    id: "countCharacters",
    title: "文字数をカウント",
    contexts: ["selection"]
  });
});

// メニュークリック時の処理
chrome.contextMenus.onClicked.addListener((info, tab) => {
  const selectedText = info.selectionText;

  switch (info.menuItemId) {
    case "convertToFullWidth":
      convertText(selectedText, "full", tab.id);
      break;
    case "convertToHalfWidth":
      convertText(selectedText, "half", tab.id);
      break;
    case "countCharacters":
      countCharacters(selectedText, tab.id);
      break;
  }
});

// テキスト変換関数
function convertText(text, type, tabId) {
  const converted = type === "full" ? 
    text.replace(/[A-Za-z0-9]/g, s => String.fromCharCode(s.charCodeAt(0) + 0xFEE0)) :
    text.replace(/[Ａ-Ｚａ-ｚ０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0));

  chrome.scripting.executeScript({
    target: { tabId: tabId },
    func: (result) => alert(result),
    args: [converted]
  });
}

// 文字数カウント関数
function countCharacters(text, tabId) {
  const total = text.length;
  const noSpaces = text.replace(/\s/g, '').length;
  const noLineBreaks = text.replace(/\n/g, '').length;

  const message = `
    総文字数: ${total}
    空白除外: ${noSpaces}
    改行除外: ${noLineBreaks}
  `;

  chrome.scripting.executeScript({
    target: { tabId: tabId },
    func: (result) => alert(result),
    args: [message]
  });
} 