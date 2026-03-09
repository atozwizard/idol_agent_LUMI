function classifyWithUpstage() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const API_KEY = 'your_key'; // 본인 키

    const ui = SpreadsheetApp.getUi();
    const lastRow = sheet.getLastRow();

    const response = ui.prompt(
        '분류할 행 범위 입력',
        `시작행, 끝행 (기본값: 2, ${lastRow})`,
        ui.ButtonSet.OK_CANCEL
    );

    if (response.getSelectedButton() !== ui.Button.OK) return;

    let startRow = 2, endRow = lastRow;
    const input = response.getResponseText().trim();

    if (input) {
        [startRow, endRow] = input.split(',').map(n => parseInt(n.trim()));
    }

    let processed = 0;
    let skipped = 0;
    let errors = 0;

    for (let i = startRow; i <= endRow; i++) {
        const userInput = sheet.getRange(i, 16).getValue(); // P열
        const aiOutput = sheet.getRange(i, 17).getValue();  // Q열
        const resultCell = sheet.getRange(i, 21);           // U열

        // 디버깅: 첫 5행만 로그
        if (i <= startRow + 4) {
            console.log(`Row ${i}: userInput="${userInput}", aiOutput="${aiOutput}", resultCell="${resultCell.getValue()}"`);
        }

        // 이미 값 있으면 스킵
        if (resultCell.getValue()) {
            skipped++;
            continue;
        }

        // 입력값 없으면 스킵
        if (!userInput && !aiOutput) {
            skipped++;
            continue;
        }

        const prompt = `다음 대화를 분류하세요.

[카테고리]
날짜 명시적으로 표시 못함
단어 오타
모델 오류
없는 노래 추천
없는 SNS 계정 추천
이전 대화 기록 불가
정상
지침을 따르지 않음

[대화]
user: ${userInput}
ai: ${aiOutput}

[규칙]
위 카테고리 중 하나만 출력. 설명 금지.

[답변]`;

        try {
            const res = UrlFetchApp.fetch('https://api.upstage.ai/v1/solar/chat/completions', {
                method: 'post',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                },
                payload: JSON.stringify({
                    model: 'solar-mini',
                    messages: [{ role: 'user', content: prompt }],
                    max_tokens: 20
                })
            });

            const result = JSON.parse(res.getContentText());
            const category = result.choices[0].message.content.trim();
            resultCell.setValue(category);
            processed++;

        } catch (e) {
            resultCell.setValue('ERROR: ' + e.message);
            errors++;
        }

        Utilities.sleep(300);
    }

    ui.alert(`완료!\n처리: ${processed}건\n스킵: ${skipped}건\n에러: ${errors}건`);
} function classifyWithUpstage() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const API_KEY = 'your_key'; // 본인 키

    const ui = SpreadsheetApp.getUi();
    const lastRow = sheet.getLastRow();

    const response = ui.prompt(
        '분류할 행 범위 입력',
        `시작행, 끝행 (기본값: 2, ${lastRow})`,
        ui.ButtonSet.OK_CANCEL
    );

    if (response.getSelectedButton() !== ui.Button.OK) return;

    let startRow = 2, endRow = lastRow;
    const input = response.getResponseText().trim();

    if (input) {
        [startRow, endRow] = input.split(',').map(n => parseInt(n.trim()));
    }

    let processed = 0;
    let skipped = 0;
    let errors = 0;

    for (let i = startRow; i <= endRow; i++) {
        const userInput = sheet.getRange(i, 16).getValue(); // P열
        const aiOutput = sheet.getRange(i, 17).getValue();  // Q열
        const resultCell = sheet.getRange(i, 21);           // U열

        // 디버깅: 첫 5행만 로그
        if (i <= startRow + 4) {
            console.log(`Row ${i}: userInput="${userInput}", aiOutput="${aiOutput}", resultCell="${resultCell.getValue()}"`);
        }

        // 이미 값 있으면 스킵
        if (resultCell.getValue()) {
            skipped++;
            continue;
        }

        // 입력값 없으면 스킵
        if (!userInput && !aiOutput) {
            skipped++;
            continue;
        }

        const prompt = `다음 대화를 분류하세요.

[카테고리]
날짜 명시적으로 표시 못함
단어 오타
모델 오류
없는 노래 추천
없는 SNS 계정 추천
이전 대화 기록 불가
정상
지침을 따르지 않음

[대화]
user: ${userInput}
ai: ${aiOutput}

[규칙]
위 카테고리 중 하나만 출력. 설명 금지.

[답변]`;

        try {
            const res = UrlFetchApp.fetch('https://api.upstage.ai/v1/solar/chat/completions', {
                method: 'post',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                },
                payload: JSON.stringify({
                    model: 'solar-mini',
                    messages: [{ role: 'user', content: prompt }],
                    max_tokens: 20
                })
            });

            const result = JSON.parse(res.getContentText());
            const category = result.choices[0].message.content.trim();
            resultCell.setValue(category);
            processed++;

        } catch (e) {
            resultCell.setValue('ERROR: ' + e.message);
            errors++;
        }

        Utilities.sleep(300);
    }

    ui.alert(`완료!\n처리: ${processed}건\n스킵: ${skipped}건\n에러: ${errors}건`);
} function classifyWithUpstage() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const API_KEY = 'your_key'; // 본인 키

    const ui = SpreadsheetApp.getUi();
    const lastRow = sheet.getLastRow();

    const response = ui.prompt(
        '분류할 행 범위 입력',
        `시작행, 끝행 (기본값: 2, ${lastRow})`,
        ui.ButtonSet.OK_CANCEL
    );

    if (response.getSelectedButton() !== ui.Button.OK) return;

    let startRow = 2, endRow = lastRow;
    const input = response.getResponseText().trim();

    if (input) {
        [startRow, endRow] = input.split(',').map(n => parseInt(n.trim()));
    }

    let processed = 0;
    let skipped = 0;
    let errors = 0;

    for (let i = startRow; i <= endRow; i++) {
        const userInput = sheet.getRange(i, 16).getValue(); // P열
        const aiOutput = sheet.getRange(i, 17).getValue();  // Q열
        const resultCell = sheet.getRange(i, 21);           // U열

        // 디버깅: 첫 5행만 로그
        if (i <= startRow + 4) {
            console.log(`Row ${i}: userInput="${userInput}", aiOutput="${aiOutput}", resultCell="${resultCell.getValue()}"`);
        }

        // 이미 값 있으면 스킵
        if (resultCell.getValue()) {
            skipped++;
            continue;
        }

        // 입력값 없으면 스킵
        if (!userInput && !aiOutput) {
            skipped++;
            continue;
        }

        const prompt = `다음 대화를 분류하세요.

[카테고리]
날짜 명시적으로 표시 못함
단어 오타
모델 오류
없는 노래 추천
없는 SNS 계정 추천
이전 대화 기록 불가
정상
지침을 따르지 않음

[대화]
user: ${userInput}
ai: ${aiOutput}

[규칙]
위 카테고리 중 하나만 출력. 설명 금지.

[답변]`;

        try {
            const res = UrlFetchApp.fetch('https://api.upstage.ai/v1/solar/chat/completions', {
                method: 'post',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                },
                payload: JSON.stringify({
                    model: 'solar-mini',
                    messages: [{ role: 'user', content: prompt }],
                    max_tokens: 20
                })
            });

            const result = JSON.parse(res.getContentText());
            const category = result.choices[0].message.content.trim();
            resultCell.setValue(category);
            processed++;

        } catch (e) {
            resultCell.setValue('ERROR: ' + e.message);
            errors++;
        }

        Utilities.sleep(300);
    }

    ui.alert(`완료!\n처리: ${processed}건\n스킵: ${skipped}건\n에러: ${errors}건`);
}
