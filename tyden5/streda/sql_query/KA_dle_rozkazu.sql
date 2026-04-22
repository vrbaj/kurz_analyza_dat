/*
	Tento skript vrací seznam unikátních kombinací Rozkaz - KA
*/
SELECT DISTINCT
	oaa.cRecorda AS CisloRozkazu,
	oaa.cControlAction AS CisloKA	
FROM MD2_VSCHT.inetuser.MDx_Order_Activity_Action oaa