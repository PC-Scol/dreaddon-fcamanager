Mail de Jean-Daniel Cazal du 18/12/2024:
> Nous n'utilisons plus le connecteur APOGEE.
> 
> L'AMUE a fourni des scripts qui traitent des CSV.
> 
> Actuellement, il n'y a pas encore d'automatisation.
> 
> Voici, la procédure actuelle :
> 
> J'utilise le client psql pour créer les CSV, à partir des tables fournies par l'addon.
> ~~~
> psql -d "host=pegase port=**** dbname=dre user=**** password=****" --csv  -c 'select * from schema_fcamanager.formation;' -o FORMATION.csv
> psql -d "host=pegase port=**** dbname=dre user=**** password=****" --csv  -c 'select * from schema_fcamanager.pia;' -o PIA.csv
> psql -d "host=pegase port=**** dbname=dre user=**** password=****" --csv  -c 'select * from schema_fcamanager.enseignement;' -o Enseignement_PIA.csv
> ~~~
> 
> Puis, je lance le script python de l'AMUE : run_all.py. Il va lancer les trois autres scripts. Toufik a corrigé les scripts, et les a adaptés à notre utilisation.
> 
> On obtient ensuite trois fichiers SQL (output_*.sql). Je les lance en base de données, l'un après l'autre dans l'ordre : activité, action, enseignement (je fais un commit après chaque script).
> 
> Je rencontre encore des erreurs sur le dernier script output_enseignement.sql.


-*- coding: utf-8 mode: markdown -*- vim:sw=4:sts=4:et:ai:si:sta:fenc=utf-8:noeol:binary