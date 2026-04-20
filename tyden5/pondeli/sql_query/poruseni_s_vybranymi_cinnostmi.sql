SELECT
    disorder.crecord,
    disorder.cAuditAction,
    audit.AuditAction AS AuditActionName,
    disorder.isCrimact,
    article.ccommodity,
    commo.Commodity AS CommodityName
FROM MD2_VSCHT.inetuser.MDx_Disorder AS disorder
LEFT JOIN MD2_VSCHT.inetuser.MDx_Article AS article
    ON article.crecordc = disorder.crecord
LEFT JOIN MD2_VSCHT.inetuser.MDx_AuditAction AS audit
    ON audit.cAuditAction = disorder.cAuditAction
LEFT JOIN MD2_VSCHT.inetuser.MDx_Commodity AS commo
    ON commo.cCommodity = article.ccommodity
WHERE disorder.exist = 1
  AND disorder.isCrimact = 1
  AND disorder.year = 2025