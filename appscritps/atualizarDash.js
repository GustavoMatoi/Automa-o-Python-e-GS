const mapa_emails_atualizacao_dashs = [
];
function atualizarDashboardsExistentes() {
  const TEMPO_LIMITE_MS = 5 * 60 * 1000; 
  const inicio = new Date().getTime();

  const sourceSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const abasParaExcluir = ["dados", "CNas", "Painel de Controle", "escolas_2025_dados", "professor_dados", "turma_dados", "idioma_dados", "horario_dados", "dia_semana_dados", "estagio_dados",
                            "escola_dados", "comentarios_dados", "sem_resposta_dados", "faixa_turma_dados", "cna_digital_school_dados" ,"dia_semana_todos_dados", "nivel_todos_dados", "idioma_todos_dados",
                            "estagio_todos_dados", "horario_todos_dados", "nivel_dados", "Links Gerados", "Logs de Envios", "dados gerais"];

  const props = PropertiesService.getScriptProperties();
  let indiceInicial = Number(props.getProperty("proximoIndice") || 0);

  Logger.log(`Retomando a partir do índice ${indiceInicial} de ${mapa_emails.length}`);

  for (let i = indiceInicial; i < mapa_emails.length; i++) {
    if (new Date().getTime() - inicio > TEMPO_LIMITE_MS) {
      props.setProperty("proximoIndice", String(i));
      Logger.log(`Tempo limite se aproximando. Parando no índice ${i}. Reagendando continuação...`);
      agendarContinuacao();
      return;
    }

    const { escola, link, analista } = mapa_emails[i];

    if (!link) {
      Logger.log(`Sem link para "${escola}" — pulei.`);
      continue;
    }

    const match = link.match(/\/d\/([a-zA-Z0-9-_]+)/);
    if (!match) {
      Logger.log(`Link inválido para "${escola}" — pulei.`);
      continue;
    }

    const tempId = match[1];
    Logger.log(`Atualizando (${i + 1}/${mapa_emails.length}): ${escola}`);

    let tempSS;
    try {
      tempSS = SpreadsheetApp.openById(tempId);
    } catch (e) {
      Logger.log(`Não consegui abrir a planilha de "${escola}": ${e.message}`);
      continue;
    }

    tempSS.getSheets().forEach(sheet => {
      if (sheet.getName().startsWith("__novo")) {
        tempSS.deleteSheet(sheet);
        Logger.log(`Removida sobra de execução anterior: ${sheet.getName()}`);
      }
    });

    const stagingFile = DriveApp.getFileById(sourceSpreadsheet.getId())
      .makeCopy(`__staging__${escola}`);
    const stagingSS = SpreadsheetApp.openById(stagingFile.getId());

    const abaRelatorioStaging = stagingSS.getSheetByName("Dashboard");
    abaRelatorioStaging.getDataRange().clearDataValidations();
    abaRelatorioStaging.getRange("A5").setValue(escola);

    SpreadsheetApp.flush();
    Utilities.sleep(5000);

    stagingSS.getSheets().forEach(sheet => {
      const range = sheet.getDataRange();
      range.copyTo(range, SpreadsheetApp.CopyPasteType.PASTE_VALUES, false);
      range.clearDataValidations();
    });

    SpreadsheetApp.flush();

    const sufixo = "__novo" + new Date().getTime() + "__";
    const nomesAntigos = tempSS.getSheets().map(s => s.getName());

    stagingSS.getSheets().forEach(stagingSheet => {
      const nome = stagingSheet.getName();
      if (abasParaExcluir.includes(nome)) return;
      stagingSheet.copyTo(tempSS).setName(sufixo + nome);
    });

    nomesAntigos.forEach(nome => {
      const aba = tempSS.getSheetByName(nome);
      if (aba) tempSS.deleteSheet(aba);
    });

    tempSS.getSheets().forEach(sheet => {
      const nomeAtual = sheet.getName();
      if (nomeAtual.startsWith(sufixo)) {
        sheet.setName(nomeAtual.replace(sufixo, ""));
      }
    });

    SpreadsheetApp.flush();

    DriveApp.getFileById(stagingFile.getId()).setTrashed(true);

    if (analista) {
      try {
        MailApp.sendEmail({
          to: analista,
          subject: `Dashboard atualizado - ${escola}`,
          htmlBody: `
            <p>Olá!</p>
            <p>O Dashboard da escola <strong>${escola}</strong> foi atualizado.</p>
            <p><a href="${link}">Acessar Dashboard</a></p>
          `
        });
        Logger.log(`E-mail enviado para o analista: ${analista}`);
      } catch (e) {
        Logger.log(`Erro ao enviar e-mail para "${analista}": ${e.message}`);
      }
    }

    Logger.log(`Dashboard atualizado: https://docs.google.com/spreadsheets/d/${tempId}/edit`);
  }

  props.deleteProperty("proximoIndice");
  removerTriggersDeContinuacao();
  Logger.log("Atualização concluída para todas as escolas.");
}

function agendarContinuacaoCriacao() {
  removerTriggersDeContinuacaoCriacao(); 
  ScriptApp.newTrigger("enviarParaListaDaPlanilha")
    .timeBased()
    .after(60 * 1000) 
    .create();
}

function removerTriggersDeContinuacaoCriacao() {
  ScriptApp.getProjectTriggers().forEach(trigger => {
    if (trigger.getHandlerFunction() === "enviarParaListaDaPlanilha"
        && trigger.getEventType() === ScriptApp.EventType.CLOCK) {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function resetarProgressoCriacao() {
  PropertiesService.getScriptProperties().deleteProperty("proximoIndiceCriacao");
  removerTriggersDeContinuacaoCriacao();
  Logger.log("Progresso de criação resetado. Próxima execução começará do zero.");
}

function getOuCriaAbaLinks(spreadsheet) {
  const nomeAba = "Links Gerados";
  let aba = spreadsheet.getSheetByName(nomeAba);

  if (!aba) {
    aba = spreadsheet.insertSheet(nomeAba);
    aba.appendRow(["Escola", "Link da Planilha"]);
    aba.setFrozenRows(1);
  }

  return aba;
}