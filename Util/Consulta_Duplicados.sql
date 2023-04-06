-- Exemplo Padrão
select count(CHID) as Quantidade, CHID from CHFingerprintImages
--where chmain.CHState = 0
group by chid
having count(CHID) >= 2

-- Contagem de Eventos por tipo
select nome.strLanguage2, events.EventHWID, count(events.EventHWID) as Quantidade  from Events
join W_Access..CfgHWEvents nome on  nome.EventHWID = events.EventHWID
group by events.EventHWID, nome.strLanguage2
having count(events.EventHWID) >= 2
order by Quantidade desc