SELECT
    d.crecord AS CisloKontroly,
    o.crecord AS CisloRozkazu,
    d.cPlaceType AS CisloMista,
    pt.PlaceType AS TypMista,
    dt.ctransport AS CisloTransportu,
    t.Transport AS TypTransportu
FROM MD2_VSCHT.inetuser.MDx_Disorder d
LEFT JOIN MD2_VSCHT.inetuser.MDx_PlaceType pt
    ON d.cPlaceType = pt.cPlaceType
LEFT JOIN MD2_VSCHT.inetuser.MDx_Disorder_Transport dt
    ON d.crecord = dt.crecordc
LEFT JOIN MD2_VSCHT.inetuser.MDx_Transport t
    ON dt.ctransport = t.cTransport
LEFT JOIN MD2_VSCHT.inetuser.MDx_Order o
    ON o.crecord = d.crecorda
ORDER BY o.crecord ASC;