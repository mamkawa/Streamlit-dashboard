function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('ドキュメント作成')
    .addItem('未作成ファイルを作成', 'createDocsFromSheet')
    .addToUi();
}

function createDocsFromSheet() {
  try {
    // スプレッドシートをIDで取得
    const ss = SpreadsheetApp.openById('1I6Akf1iU46LcE72HMpW3sxvAvXbyJRUYatIU_p4Hg2o');
    if (!ss) {
      throw new Error('スプレッドシートが取得できません。IDを確認してください。');
    }

    // アクティブなシートを取得
    const sheet = ss.getActiveSheet();
    if (!sheet) {
      throw new Error('シートが見つかりません。');
    }
    Logger.log('シート名: ' + sheet.getName());
    
    // 保存先フォルダの取得
    const targetFolderId = '1Ul0IyQdKNNU3F2MyhYZuo5U2xw-pXCvm';
    const targetFolder = DriveApp.getFolderById(targetFolderId);
    Logger.log('フォルダの取得に成功しました: ' + targetFolder.getName());

    // テータ範囲を取得
    const dataRange = sheet.getDataRange();
    const values = dataRange.getValues();

    // ヘッダー行をスキップして2行目から処理
    let createdDocs = 0;
    for (let i = 1; i < values.length; i++) {
      const fileName = values[i][1];  // B列：ファイル名
      const content = values[i][2];   // C列：本文
      const isCreated = values[i][3];  // D列：作成済チェックボックス

      // チェックボックスがfalse（未チェック）の場合のみ処理
      if (!isCreated) {
        Logger.log(`処理中のデータ - ファイル名: [${fileName}], 本文: [${content}]`);
        
        try {
          // 新規ドキュメントを作成
          const doc = DocumentApp.create(fileName);
          Logger.log(`ドキュメント作成成功: ${fileName}`);
          
          // ドキュメントの本文を取得して内容を書き込む
          const body = doc.getBody();
          body.setText(content);
          
          // ドキュメントを保存
          doc.saveAndClose();
          
          // 作成したドキュメントを指定フォルダに移動
          const docFile = DriveApp.getFileById(doc.getId());
          targetFolder.addFile(docFile);
          DriveApp.getRootFolder().removeFile(docFile);
          
          // チェックボックスをtrueに設定
          sheet.getRange(i + 1, 4).setValue(true);  // D列（4列目）にチェックを入れる
          
          createdDocs++;
          Logger.log(`ドキュメント "${fileName}" を作成し、フォルダに移動しました（${i}/${values.length - 1}）`);
        } catch (docError) {
          Logger.log(`エラー - ドキュメント "${fileName}" の処理中: ${docError.message}`);
        }
      }
    }
    
    Logger.log(`処理が完了しました。${createdDocs}個のドキュメントを作成しました。`);
    
    if (createdDocs === 0) {
      Logger.log('警告: ドキュメントが1つも作成されませんでした。');
    }
  } catch (error) {
    Logger.log('エラーが発生しました: ' + error.message);
    throw error;
  }
} 