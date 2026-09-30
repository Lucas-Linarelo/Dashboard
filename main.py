import sys
import os
import glob
import re
import pandas as pd
from datetime import datetime

def limpar_dados_cobranca(df):
    """Padroniza datas e valores financeiros do dataset."""
    df['DT_VENCIMENTO'] = pd.to_datetime(df['DT_VENCIMENTO'], format='mixed', dayfirst=True)
    
    for col in ['VALOR_PARCELA', 'VALOR_PAGO']:
        df[col] = (df[col]
                   .astype(str)
                   .str.replace('.', '', regex=False)
                   .str.replace(',', '.', regex=False)
                   .astype(float))
    return df

def gerar_relatorio_inadimplencia(caminho_csv, data_analise):
    """Filtra inadimplentes, gera o CSV filtrado e o Dashboard HTML interativo."""
    print("A carregar e limpar os dados...")
    df = pd.read_csv(caminho_csv, sep=';')
    df = limpar_dados_cobranca(df)
    
    df_inad = df[
        (df['STATUS_PARCELA'] == 'ABERTA') & 
        (df['DT_VENCIMENTO'] < pd.to_datetime(data_analise)) &
        (df['SITUACAO_CONTRATO'] == 'ATIVO')
    ].copy()
    
    df_inad['VALOR_DEVIDO'] = df_inad['VALOR_PARCELA'] - df_inad['VALOR_PAGO']
    
    df_resumo = df_inad.groupby(
        ['EMPREENDIMENTO', 'NUM_CONTRATO', 'CLIENTE', 'TELEFONE']
    ).agg({
        'VALOR_DEVIDO': 'sum',
        'DT_VENCIMENTO': 'min',
        'NUM_ACORDO': lambda x: x.dropna().iloc[0] if not x.dropna().empty else ''
    }).reset_index()
    
    df_resumo = df_resumo.sort_values(by=['EMPREENDIMENTO', 'VALOR_DEVIDO'], ascending=[True, False])
    
    # Prepara a pasta de saída
    pasta_saida = 'Arquivo Final'
    os.makedirs(pasta_saida, exist_ok=True)
    
    # 1. Guarda os dados filtrados em formato CSV
    nome_saida_csv = os.path.join(pasta_saida, f'dados_filtrados_{data_analise}.csv')
    df_resumo.to_csv(nome_saida_csv, index=False, sep=';', encoding='utf-8-sig')
    
    linhas_html = ""
    for index, row in df_resumo.iterrows():
        emp = row['EMPREENDIMENTO']
        contrato = str(row['NUM_CONTRATO'])
        cli = row['CLIENTE']
        tel = row['TELEFONE']
        acordo = row['NUM_ACORDO']
        vencimento_dt = row['DT_VENCIMENTO']
        
        vencimento_br = vencimento_dt.strftime('%d/%m/%Y')
        vencimento_sort = vencimento_dt.strftime('%Y%m%d')
        
        valor_br = f"{row['VALOR_DEVIDO']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        valor_sort = f"{row['VALOR_DEVIDO']:.2f}"
        
        row_id = f"cobrado_{contrato}"
        
        if pd.notna(acordo) and str(acordo).strip() != '':
            texto_copiar = f"{emp}, {cli}, {tel}; Contrato: {contrato}, Vencimento: {vencimento_br}, Acordo: {acordo}, Valor Devido R${valor_br}"
            badge_acordo = f'<span class="badge-acordo" style="background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; display: inline-block;">Acordo: {acordo}</span>'
        else:
            texto_copiar = f"{emp}, {cli}, {tel}; Contrato: {contrato}, Vencimento: {vencimento_br}, Valor Devido R${valor_br}"
            badge_acordo = '<span style="color: #9ca3af; font-size: 0.8rem;">Sem acordo</span>'
        
        tel_limpo = ''.join(filter(str.isdigit, str(tel)))
        if len(tel_limpo) >= 10 and not tel_limpo.startswith('55'):
            tel_limpo = '55' + tel_limpo
            
        link_whatsapp = f"https://wa.me/{tel_limpo}?text=Olá%20{cli},%20notamos%20uma%20pendência%20vencida%20em%20{vencimento_br}%20no%20contrato%20{contrato}%20do%20{emp}."
        
        linhas_html += f"""
                <tr id="tr_{row_id}">
                    <td style="text-align: center; width: 40px;" data-sort="0">
                        <input type="checkbox" id="{row_id}" onchange="marcarCobrado('{row_id}')" style="cursor: pointer; width: 16px; height: 16px;">
                    </td>
                    <td>{emp}</td>
                    <td>{contrato}</td>
                    <td>{cli}</td>
                    <td><a href="{link_whatsapp}" target="_blank" title="Abrir no WhatsApp" style="color: #2563eb; text-decoration: none; font-weight: 500;">{tel}</a></td>
                    <td data-sort="{vencimento_sort}">{vencimento_br}</td>
                    <td data-sort="{valor_sort}">R$ {valor_br}</td>
                    <td>{badge_acordo}</td>
                    <td style="text-align: center;">
                        <button onclick="copiarTexto('{texto_copiar}')" class="btn-copiar">Copiar Mensagem</button>
                    </td>
                </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard de Inadimplência</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; color: #333; padding: 20px; margin: 0; box-sizing: border-box; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        
        .container {{ width: 96%; max-width: 1550px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; overflow-x: auto; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9rem; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; vertical-align: middle; white-space: nowrap; }}
        
        th.sortable {{ background-color: #f3f4f6; font-weight: 600; color: #4b5563; position: sticky; top: 0; cursor: pointer; user-select: none; }}
        th.sortable:hover {{ background-color: #e5e7eb; }}
        th.sortable::after {{ content: " ↕"; font-size: 0.8rem; color: #9ca3af; }}

        th.static {{ background-color: #f3f4f6; font-weight: 600; color: #4b5563; position: sticky; top: 0; user-select: none; }}
        
        .btn-copiar {{ padding: 8px 12px; cursor: pointer; background: #2563eb; color: white; border: none; border-radius: 4px; font-size: 0.85rem; font-weight: 500; transition: background 0.2s; }}
        .btn-copiar:hover {{ background: #1d4ed8; }}
        
        .linha-cobrada {{ background-color: #f3f4f6 !important; color: #9ca3af; text-decoration: line-through; }}
        .linha-cobrada a {{ color: #9ca3af !important; text-decoration: none; }}
        .linha-cobrada .badge-acordo {{ text-decoration: none !important; }}

        .toast {{ visibility: hidden; min-width: 250px; background-color: #111827; color: #fff; text-align: center; border-radius: 6px; padding: 16px; position: fixed; z-index: 1; bottom: 30px; left: 50%; transform: translateX(-50%); font-size: 0.95rem; font-weight: 500; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .toast.show {{ visibility: visible; animation: fadein 0.3s, fadeout 0.3s 2.5s; }}
        @keyframes fadein {{ from {{bottom: 0; opacity: 0;}} to {{bottom: 30px; opacity: 1;}} }}
        @keyframes fadeout {{ from {{bottom: 30px; opacity: 1;}} to {{bottom: 0; opacity: 0;}} }}
        .resumo {{ display: flex; gap: 20px; background: #f3f4f6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .resumo div {{ flex: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="margin-top: 0; margin-bottom: 0; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px;">Dashboard de Cobrança - Caprem</h2>
        
        <div class="resumo" style="margin-top: 20px;">
            <div><span style="color: #6b7280; font-size: 0.85rem;">Total em Dívida</span><br><strong style="font-size: 1.25rem; color: #b91c1c;">R$ {df_inad['VALOR_DEVIDO'].sum():,.2f}</strong></div>
            <div><span style="color: #6b7280; font-size: 0.85rem;">Clientes para Contactar</span><br><strong style="font-size: 1.25rem; color: #1d4ed8;">{df_resumo['CLIENTE'].nunique()}</strong></div>
            <div><span style="color: #6b7280; font-size: 0.85rem;">Data de Análise</span><br><strong style="font-size: 1.25rem; color: #111827;">{data_analise}</strong></div>
        </div>

        <table id="tabelaCobranca">
            <thead>
                <tr>
                    <th class="sortable" onclick="sortTable(this)" title="Atenção: As marcações de checkboxes são salvas apenas localmente neste computador e navegador. Não sincronizam com cópias enviadas a outros utilizadores.">✓</th>
                    <th class="sortable" onclick="sortTable(this)">Empreendimento</th>
                    <th class="sortable" onclick="sortTable(this)">Contrato</th>
                    <th class="sortable" onclick="sortTable(this)">Cliente</th>
                    <th class="static">Telefone</th>
                    <th class="sortable" onclick="sortTable(this)">Vencimento Mais Antigo</th>
                    <th class="sortable" onclick="sortTable(this)">Valor Devido</th>
                    <th class="sortable" onclick="sortTable(this)">Situação Acordo</th>
                    <th class="static" style="text-align: center;">Ação</th>
                </tr>
            </thead>
            <tbody>{linhas_html}
            </tbody>
        </table>
    </div>
    
    <div id="toast" class="toast">Texto copiado para a área de transferência!</div>
    
    <script>
        const dataAnaliseGlobal = "{data_analise}";

        function copiarTexto(texto) {{
            navigator.clipboard.writeText(texto).then(function() {{
                var x = document.getElementById("toast");
                x.className = "toast show";
                setTimeout(function(){{ x.className = x.className.replace("toast show", "toast"); }}, 2800);
            }}, function(err) {{
                alert('Erro ao copiar: ' + err);
            }});
        }}

        function sortTable(thElement) {{
            var table = document.getElementById("tabelaCobranca");
            var tbody = table.getElementsByTagName("tbody")[0];
            var n = thElement.cellIndex;
            var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            
            switching = true;
            dir = thElement.getAttribute("data-dir") === "asc" ? "desc" : "asc";
            
            var headers = table.getElementsByTagName("TH");
            for (var h = 0; h < headers.length; h++) {{
                headers[h].removeAttribute("data-dir");
            }}
            thElement.setAttribute("data-dir", dir);

            while (switching) {{
                switching = false;
                rows = tbody.rows;
                
                for (i = 0; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    
                    let xVal, yVal;
                    if (n === 0) {{
                        const cbX = rows[i].querySelector("input[type='checkbox']");
                        const cbY = rows[i + 1].querySelector("input[type='checkbox']");
                        xVal = cbX && cbX.checked ? 1 : 0;
                        yVal = cbY && cbY.checked ? 1 : 0;
                    }} else {{
                        xVal = x && x.hasAttribute("data-sort") ? parseFloat(x.getAttribute("data-sort")) : (x ? x.innerText.toLowerCase() : "");
                        yVal = y && y.hasAttribute("data-sort") ? parseFloat(y.getAttribute("data-sort")) : (y ? y.innerText.toLowerCase() : "");
                    }}

                    if (dir == "asc") {{
                        if (xVal > yVal) {{ shouldSwitch = true; break; }}
                    }} else if (dir == "desc") {{
                        if (xVal < yVal) {{ shouldSwitch = true; break; }}
                    }}
                }}
                
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }}
            }}
        }}

        function marcarCobrado(rowId) {{
            const checkbox = document.getElementById(rowId);
            const row = document.getElementById("tr_" + rowId);
            const tdFlag = row.getElementsByTagName("TD")[0];
            const chaveStorage = dataAnaliseGlobal + "_" + rowId;
            
            if (checkbox.checked) {{
                row.classList.add("linha-cobrada");
                tdFlag.setAttribute("data-sort", "1");
                localStorage.setItem(chaveStorage, "true");
            }} else {{
                row.classList.remove("linha-cobrada");
                tdFlag.setAttribute("data-sort", "0");
                localStorage.setItem(chaveStorage, "false");
            }}
        }}

        window.onload = function() {{
            const checkboxes = document.querySelectorAll("input[type='checkbox']");
            checkboxes.forEach(cb => {{
                const chaveStorage = dataAnaliseGlobal + "_" + cb.id;
                const savedState = localStorage.getItem(chaveStorage);
                const row = document.getElementById("tr_" + cb.id);
                const tdFlag = row ? row.getElementsByTagName("TD")[0] : null;
                
                if (savedState === "true") {{
                    cb.checked = true;
                    if (row) row.classList.add("linha-cobrada");
                    if (tdFlag) tdFlag.setAttribute("data-sort", "1");
                }} else {{
                    if (tdFlag) tdFlag.setAttribute("data-sort", "0");
                }}
            }});
        }};
    </script>
</body>
</html>"""

    nome_saida_html = os.path.join(pasta_saida, f'dashboard_inadimplencia_{data_analise}.html')
    with open(nome_saida_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    abs_path = os.path.abspath(nome_saida_html)
    print("==================================================")
    print(f"Relatório HTML e CSV gerados com sucesso na pasta '{pasta_saida}'!")
    print(f"file:///{abs_path.replace(os.sep, '/')}")
    print("==================================================")
    
    os.system(f'start "" "{nome_saida_html}"')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arquivo_escolhido = sys.argv[1]
    else:
        print("Nenhum arquivo foi passado como parâmetro.")
        arquivos_csv = glob.glob(os.path.join("Arquivo Original", "*.csv"))
        
        if not arquivos_csv:
            print("ERRO: Nenhum arquivo .csv encontrado na pasta 'Arquivo Original'.")
            sys.exit(1)
            
        print("\nArquivos disponíveis na pasta 'Arquivo Original':")
        for i, arq in enumerate(arquivos_csv):
            print(f"[{i+1}] {arq}")
            
        escolha = input("\nDigite o número do arquivo que deseja processar: ")
        try:
            indice = int(escolha) - 1
            arquivo_escolhido = arquivos_csv[indice]
        except (ValueError, IndexError):
            print("Erro: Escolha inválida. Encerrando o programa.")
            sys.exit(1)
            
    match_data = re.search(r'\d{4}-\d{2}-\d{2}', arquivo_escolhido)
    data_referencia = match_data.group(0) if match_data else datetime.today().strftime('%Y-%m-%d')
    
    gerar_relatorio_inadimplencia(arquivo_escolhido, data_referencia)