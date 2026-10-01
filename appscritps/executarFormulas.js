const ID_PLANILHA = ""; 

function doGet(e) {
  return executarFormulas();
}

function getSheetByGid(planilha, gid) {
  return planilha.getSheets().find(s => s.getSheetId() === Number(gid));
}

function executarFormulas() {
  const planilha = SpreadsheetApp.openById(ID_PLANILHA);
  const GID_DASHBOARD = "1096839784";

  const dados = [
   
  ];

  "ABCDEFGHIJKLMNO".split("").forEach(col => {
    dados.push({
      planilha: GID_DASHBOARD,
      celula: `${col}17`,
      formula: `=cna_digital_school_dados!${col}2`
    });
  });

  const erros = [];

    console.log("Localidade da planilha: " + planilha.getSpreadsheetLocale());

  for (const aba of dados) {
    const pagina = getSheetByGid(planilha, aba.planilha);
    if (!pagina) {
      erros.push(`Aba com gid ${aba.planilha} não encontrada (${aba.celula})`);
      continue;
    }

    const celula = pagina.getRange(aba.celula);
    const comVirgula = aba.formula.replace(/;/g, ",");
    const comPontoVirgula = aba.formula.replace(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/g, ";");

    try {
      celula.setFormula(comVirgula);
      SpreadsheetApp.flush();

      if (String(celula.getDisplayValue()).startsWith("#ERROR")) {
        celula.setFormula(aba.formula); 
        SpreadsheetApp.flush();
      }

      if (String(celula.getDisplayValue()).startsWith("#ERROR")) {
        erros.push(`${pagina.getName()}!${aba.celula}: #ERROR! nas duas sintaxes`);
      }
    } catch (err) {
      erros.push(`${pagina.getName()}!${aba.celula}: ${err.message}`);
    }
  }

  SpreadsheetApp.flush();

  if (erros.length) {
    console.error(erros.join("\n"));
    return ContentService.createTextOutput("Concluído com erros:\n" + erros.join("\n"));
  }

  return ContentService.createTextOutput("Fórmula executada com sucesso!");
}