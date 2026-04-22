/* 
	Tento skript zjišťuje nařízené KČ pro jednotlivé rozkazy.
*/
SELECT 
	aaa.cRecorda AS CisloRozkazu,
	STRING_AGG(aaa.cAuditAction, ',') AS NarizeneKC
FROM MD2_VSCHT.inetuser.MDx_Activity_AuditAction aaa
LEFT JOIN MD2_VSCHT.inetuser.MDx_Order_Activity_Action oaa
	ON oaa.cRecordA = aaa.cRecorda
GROUP BY aaa.cRecorda
ORDER BY aaa.cRecorda DESC