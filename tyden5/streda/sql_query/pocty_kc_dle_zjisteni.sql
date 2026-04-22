/* 
	Skript pro zjištění všech provedených kontrolních úkonů a 
	jejich kontrolních činností pro jednotlivé rozkazy. Vnější 
	SELECT agerguje data z předchozího SELECTu tak, že podle sloupečku 
	Poruseni sloučí KČ pro jednotlivá čísla kontrolních úkonů, čímž 
	získáme dvoa sloupce - KČ s pozitivním a negativním zjištěním. 
	Dále se pro případné další využití počítají počty KČ v každém ze sloupců. 
*/
SELECT
	t.CisloRozkazu,
	COUNT(CASE WHEN t.Poruseni = 0 THEN CAST(t.KCvDAA AS varchar(max)) END) AS PocetNegativnichKC,
	COUNT(CASE WHEN t.Poruseni = 1 THEN CAST(t.KCvDAA AS varchar(max)) END) AS PocetPozitivnichKC,
	STRING_AGG(CASE WHEN t.Poruseni = 0 THEN CAST(t.KCvDAA AS varchar(max)) END, ',') AS NegativniKC,
	STRING_AGG(CASE WHEN t.Poruseni = 1 THEN CAST(t.KCvDAA AS varchar(max)) END, ',') AS PozitivniKC
FROM
(
	/* 
		Tento SELECT vrací sloučené tabulky MDx_Disorder a MDx_Disorder_AuditAction (1:n) přes číslo 
		kontrolního úkonu (crecord / crecordc). Cílem je napárovat na sebe číslo kontrolního úkonu, číslo KČ v tabulce 
		MDx_Disorder a číslo KČ v tabulce MDx_Disorder_auditAction. V případě shody těchto čísel se jedná o KČ 
		s pozitivním zjištěním, v případě neshody se jedná o KČ bez pozitivního zjištění. Tabulka dále slouží 
		pro agregaci čísel KČ  s / bez pozitivního zjištění do jednoho sloupce. 
	*/
	SELECT 
		d.crecorda AS CisloRozkazu, 
		daa.cAuditAction AS KCvDAA,
		/* 
			Vyšetření shody kontrolní činnosti mezi MDx_Disorder a MDx_DisorderAuditAction 
				- pokud je shodné -> pozitivní zjištění u dané KČ v MDx_Disorder_AuditAction
				- pokud není shodné -> bez pozitivního zjištění u dané KČ v MDx_Disorder_AuditAction
					- isCrimact = 0 -> jedná se o KČ bez pozitivního zjištění
					- isCrimact = 1 -> jedná se o KČ bez pozitvního zjištění, 
						kde JINÁ KČ u stejného záznamu v MDx_Disorder vedla k pozitivnímu zjištění
		*/
		CASE 
			WHEN d.cAuditAction = daa.cAuditAction THEN 1
			ELSE 0
		END AS Poruseni		
	FROM MD2_VSCHT.inetuser.MDx_Disorder d
	LEFT JOIN MD2_VSCHT.inetuser.MDx_Disorder_AuditAction daa
		ON daa.cRecordc = d.crecord
	WHERE d.isForCoop = 0 
) t
GROUP BY t.CisloRozkazu
ORDER BY t.CisloRozkazu DESC
