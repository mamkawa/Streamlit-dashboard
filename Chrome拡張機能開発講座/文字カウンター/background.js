// 拡張機能がインストールされたときに右クリックメニューを作成
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "countCharacters",
    title: "選択テキストの文字数をカウント",
    contexts: ["selection"]
  });
});

// 右クリックメニューがクリックされたときの処理
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "countCharacters") {
    const selectedText = info.selectionText;
    const characterCount = selectedText.length;
    const message = `選択されたテキストの文字数: ${characterCount}文字`;
    
    // アラートで文字数を表示
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (messageText) => {
        alert(messageText);
      },
      args: [message]
    });
  }
});