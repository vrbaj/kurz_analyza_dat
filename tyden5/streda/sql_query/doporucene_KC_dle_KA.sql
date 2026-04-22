/*
    Skript pro zjištění všech doporučených kontrolních činností pro jednotlivé 
    kontrolní akce. Vnější SELECT agreguje data přes číslo KA tak, že vytvoří seznam všech unikátních 
    doporučených KČ pro každou unikátní KA   
*/
SELECT
    t.CisloKA,
    STRING_AGG(t.DoporuceneKC, ',') AS DoporuceneKC
FROM
(
    /*
        Tento SELECT sloučí tabulky MDx_D_CA_Mor a Cinnosti_Doporuceni přes číslo jednací.
        Následně odfiltruje pryč ty záznamy, které nejsou v tabulce Cinnosti_Doporuceni
        (nemají doporučené KČ). Jelikož nelze navázat čísla jednací na konkrétní KA / rozkazy,
        zachovávají se pouze unikátní kombinace KA - KČ.
    */
    SELECT DISTINCT
        dcm.cControlAction AS CisloKA,
        cd.ID_AuditAction AS DoporuceneKC
    FROM MD2_VSCHT.inetuser.MDx_D_CA_Mor dcm
    LEFT JOIN MD2_VSCHT.diana.Cinnosti_Doporuceni cd
        ON cd.DoporuceniCislo = dcm.cj
    WHERE cd.ID_AuditAction IS NOT NULL
) t
GROUP BY t.CisloKA
ORDER BY t.CisloKA DESC