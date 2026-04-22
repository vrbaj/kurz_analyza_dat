SELECT d.axisx, d.axisy, a.AuditAction, d.isCrimact
FROM inetuser.MDx_Disorder d
LEFT JOIN inetuser.MDx_AuditAction a ON d.cAuditAction = a.cAuditAction