import re
import sys

##--------------------EXPRESIONES REGULARES------------------

entero = re.compile('^[0-9]+$')
flotante = re.compile('^[0-9]+[.][0-9]*$')
identificador = re.compile('^(([a-zA-Z])+[0-9]*)+$')
tokensreservados1 = re.compile('^({$|}$|,$|:$|#$|\[$|\]$|\($|\)$|>$|<$|!$|\+$|-$|\*$|/$|%$|\^$|=$|\.$)+')
tokensreservados2 = re.compile('^(>=$|<=$|==$|!=$|&&$|\|\|$)+')
tokensLargos = re.compile('^(desde$|todo$|end$|retorno$|true$|false$|funcion$|retorno$|log$|end$|for$|while$|if$|in$|importar$|else$|nil$|leer$|elif$)+')
comentario = re.compile('^#.*')
stringCompleta = re.compile('^\".*\"$')
stringIncompleta = re.compile('^\".*')
espacios = re.compile('^(\ +|\n+|\t)+')

diccionarioTokens={'{':'token_llave_izq','}':'token_llave_der','#':'token_com','[':'token_cor_izq',']':'token_cor_der','(':'token_par_izq',')':'token_par_der','>':'token_mayor','<':'token_menor','.':'token_point','!':'token_not','+':'token_mas','-':'token_menos','*':'token_mul','/':'token_div','%':'token_mod','^':'token_pot','=':'token_assign','>=':'token_mayor_igual','<=':'token_menor_igual','==':'token_igual_num','!=':'token_diff_num','&&':'token_and','||':'token_or',',':'token_coma',':':'token_dosp','\.':'token_point'}

##------------------PILA DEL PROGRAMA-----------------------

pila=[];
pos=[];
content=[];

##-----------------CONJUNTOS DE PREDICCION------------------

ARRAY={}
OBJETO={}
VARIABLE={}
EXPR={}
EXPR2={}
FACTOREXPR2={}
AUXP={}
AUXF={}
PARAM={}
FACTORAUXP={}

ATOM={
  '<token_integer>':['<token_integer>'],
  '<token_float>':['<token_float>'],
  '<true>':['<true>'],
  '<false>':['<false>'],
  '<token_string>':['<token_string>'],
  '<token_cor_izq>':["ARRAY"],
  '<token_llave_izq>':["OBJETO"],
  '<id>':["VARIABLE"],
  '<nil>':['<nil>']
}

EXPRCOMA={
  '<token_menos>':['<token_menos>',"EXPR"],
  '<token_not':["EXPR"],
  '<token_par_izq>':["EXPR"],
  '<token_integer>':["EXPR"],
  '<token_float>':["EXPR"],
  '<true>':["EXPR"],
  '<false>':["EXPR"],
  '<token_string>':["EXPR"],
  '<nil>':["EXPR"],
  '<token_llave_izq>':["EXPR"],
  '<id>':["EXPR"],
  '<token_cor_izq>':["EXPR"]
}

EXPR={
  '<token_not>':["EXPR2","FACTOREXPR2"],
  '<token_par_izq>':["EXPR2","FACTOREXPR2"],
  '<token_integer>':["EXPR2","FACTOREXPR2"],
  '<token_float>':["EXPR2","FACTOREXPR2"],
  '<true>':["EXPR2","FACTOREXPR2"],
  '<false>':["EXPR2","FACTOREXPR2"],
  '<token_string>':["EXPR2","FACTOREXPR2"],
  '<nil>':["EXPR2","FACTOREXPR2"],
  '<token_llave_izq>':["EXPR2","FACTOREXPR2"],
  '<id>':["EXPR2","FACTOREXPR2"],
  '<token_cor_izq>':["EXPR2","FACTOREXPR2"],
  '<token_menos>':["EXPRCOMA"]
}

EXPR2={
  '<token_not>':['<token_not>',"EXPR2"],
  '<token_par_izq>':['<token_par_izq>',"EXPRCOMA",'<token_par_der>'],
  '<token_integer>':['ATOM'],
  '<token_float>':['ATOM'],
  '<true>':['ATOM'],
  '<false>':['ATOM'],
  '<token_string>':['ATOM'],
  '<nil>':['ATOM'],
  '<token_llave_izq>':['ATOM'],
  '<id>':['ATOM'],
  '<token_cor_izq>':['ATOM']
}


FACTOREXPR2={
  '<token_mul>':['<token_mul>', 'EXPR'],
  '<token_div>':['<token_div>', 'EXPR'],
  '<token_mod>':['<token_mod>', 'EXPR'],
  '<token_mas>':['<token_mas>', 'EXPR'],
  '<token_menos>':['<token_menos>', 'EXPR'],
  '<token_mayor_igual>':['<token_mayor_igual>', 'EXPR'],
  '<token_menor_igual>':['<token_menor_igual>', 'EXPR'],
  '<token_mayor>':['<token_mayor>', 'EXPR'],
  '<token_menor>':['<token_menor>', 'EXPR'],
  '<token_igual_num>':['<token_igual_num>', 'EXPR'],
  '<token_diff_num>':['<token_diff_num>', 'EXPR'],
  '<token_and>':['<token_and>', 'EXPR'],
  '<token_or>':['<token_or>', 'EXPR'],
  '<token_pot>':['<token_pot>', 'EXPR'],
  '<token_coma>':['epsilon'],
  '<token_not>':['epsilon'],
  '<token_par_izq>':['epsilon'],
  '<token_integer>':['epsilon'],
  '<token_float>':['epsilon'],
  '<true>':['epsilon'],
  '<false>':['epsilon'],
  '<token_string>':['epsilon'],
  '<nil>':['epsilon'],
  '<token_cor_izq>':['epsilon'],
  '<id>':['epsilon'],
  '<token_llave_izq>':['epsilon'],
  '<token_cor_der>':['epsilon'],
  '<token_par_der>':['epsilon'],
  '<token_point>':['epsilon'],
  '<importar>':['epsilon'],
  '<desde>':['epsilon'],
  '<leer>':['epsilon'],
  '<log>':['epsilon'],
  '<retorno>':['epsilon'],
  '<if>':['epsilon'],
  '<for>':['epsilon'],
  '<while>':['epsilon'],
  '<funcion>':['epsilon'],
  '<enter>':['epsilon'],
  '<token_dosp>':['epsilon'],
  '<token_llave_der>':['epsilon'],
  '<end>':['epsilon']
}

FUN_STAT={
  '<funcion>':['<funcion>','<id>','<token_par_izq>','AUXP','<token_par_der>','AUXF','<end>','<funcion>']
}

AUXP={
  '<id>':['PARAM','FACTORAUXP'],
  '<token_par_der>':['epsilon']
}

PARAM={
  '<id>':['<id>','FACTORPARAM']
}

FACTORAUXP={
  '<token_coma>':['<token_coma>','AUXP'],
  '<token_par_der>':['epsilon']
}

FACTORPARAM={
  '<token_igual_num>':['<token_igual_num>','EXPR'],
  '<token_coma>':['epsilon'],
  '<token_par_der>':['epsilon']
}

AUXF={
  '<enter>':['<enter>','AUXF'],
  '<token_point>':['STAT','AUXF'],
  '<id>':['STAT','AUXF'],
  '<importar>':['STAT','AUXF'],
  '<desde>':['STAT','AUXF'],
  '<log>':['STAT','AUXF'],
  '<leer>':['STAT','AUXF'],
  '<retorno>':['STAT','AUXF'],
  '<token_integer>':['STAT','AUXF'],
  '<token_float>':['STAT','AUXF'],
  '<true>':['STAT','AUXF'],
  '<false>':['STAT','AUXF'],
  '<token_string>':['STAT','AUXF'],
  '<nil>':['STAT','AUXF'],
  '<token_llave_izq>':['STAT','AUXF'],
  '<token_cor_izq>':['STAT','AUXF'],
  '<if>':['STAT','AUXF'],
  '<for>':['STAT','AUXF'],
  '<while>':['STAT','AUXF'],
  '<funcion>':['STAT','AUXF'],
  '<end>':['epsilon'],
  '<token_llave_der>':['epsilon']
}

ARRAY={
  '<token_cor_izq>':['<token_cor_izq>','INTERNARRAY','<token_cor_der>']
}

INTERNARRAY={
  '<token_not>':['EXPR','INTERNARRAYP'],
  '<token_par_izq>':['EXPR','INTERNARRAYP'],
  '<token_integer>':['EXPR','INTERNARRAYP'],
  '<token_float>':['EXPR','INTERNARRAYP'],
  '<true>':['EXPR','INTERNARRAYP'],
  '<false>':['EXPR','INTERNARRAYP'],
  '<token_string>':['EXPR','INTERNARRAYP'],
  '<nil>':['EXPR','INTERNARRAYP'],
  '<token_cor_izq>':['EXPR','INTERNARRAYP'],
  '<id>':['EXPR','INTERNARRAYP'],
  '<token_llave_izq>':['EXPR','INTERNARRAYP'],
  '<token_cor_der':['epsilon']
}

INTERNARRAYP={
  '<token_coma>':['INTERNARRAY1'],
  '<token_cor_der>':['INTERNARRAY1'],
  '<token_dosp>':['INTERNARRAY2']
}

INTERNARRAY1={
  '<token_coma>':['<token_coma>','EXPR','INTERNARRAY1'],
  '<token_cor_der>':['epsilon']
}

INTERNARRAY2={
  '<token_dosp>':['<token_dosp>','INTERNARRAY3']
}

INTERNARRAY3={
  '<token_not>':['EXPR','INTERNARRAY3P'],
  '<token_par_izq>':['EXPR','INTERNARRAY3P'],
  '<token_integer>':['EXPR','INTERNARRAY3P'],
  '<token_float>':['EXPR','INTERNARRAY3P'],
  '<true>':['EXPR','INTERNARRAY3P'],
  '<false>':['EXPR','INTERNARRAY3P'],
  '<token_string>':['EXPR','INTERNARRAY3P'],
  '<nil>':['EXPR','INTERNARRAY3P'],
  '<token_cor_izq>':['EXPR','INTERNARRAY3P'],
  '<id>':['EXPR','INTERNARRAY3P'],
  '<token_llave_izq>':['EXPR','INTERNARRAY3P']
}

INTERNARRAY3P={
  '<token_dosp>':['<token_dosp>','<EXPR>'],
  '<token_cor_der>':['epsilon']
}

SOURCE={
  '<enter>':['FROM_FILE'],
  '<EOF>':['FROM_FILE'],
  '<token_point>':['FROM_FILE'],
  '<id>':['FROM_FILE'],
  '<importar>':['FROM_FILE'],
  '<desde>':['FROM_FILE'],
  '<leer>':['FROM_FILE'],
  '<log>':['FROM_FILE'],
  '<retorno>':['FROM_FILE'],
  '<token_integer>':['FROM_FILE'],
  '<token_float>':['FROM_FILE'],
  '<true>':['FROM_FILE'],
  '<false>':['FROM_FILE'],
  '<token_string>':['FROM_FILE'],
  '<nil>':['FROM_FILE'],
  '<token_cor_izq>':['FROM_FILE'],
  '<token_llave_izq>':['FROM_FILE'],
  '<if>':['FROM_FILE'],
  '<for>':['FROM_FILE'],
  '<while>':['FROM_FILE'],
  '<funcion>':['FROM_FILE'],
  '<token_menos>':['STAT','FROM_FILE']
}

FROM_FILE={
  '<leer>':['STAT','FROM_FILE'],
  '<token_point>':['STAT','FROM_FILE'],
  '<id>':['STAT','FROM_FILE'],
  '<importar>':['STAT','FROM_FILE'],
  '<desde>':['STAT','FROM_FILE'],
  '<log>':['STAT','FROM_FILE'],
  '<retorno>':['STAT','FROM_FILE'],
  '<token_integer>':['STAT','FROM_FILE'],
  '<token_float>':['STAT','FROM_FILE'],
  '<true>':['STAT','FROM_FILE'],
  '<false>':['STAT','FROM_FILE'],
  '<token_string>':['STAT','FROM_FILE'],
  '<nil>':['STAT','FROM_FILE'],
  '<token_cor_izq>':['STAT','FROM_FILE'],
  '<token_llave_izq>':['STAT','FROM_FILE'],
  '<if>':['STAT','FROM_FILE'],
  '<for>':['STAT','FROM_FILE'],
  '<while>':['STAT','FROM_FILE'],
  '<funcion>':['STAT','FROM_FILE'],
  '<enter>':['<enter>','FROM_FILE'],
  '<token_menos>':['STAT','FROM_FILE'],
  '<EOF>':['<EOF>']
}

STAT={
  '<leer>':['SIMPLE_STAT'],
  '<token_point>':['SIMPLE_STAT'],
  '<id>':['SIMPLE_STAT'],
  '<importar>':['SIMPLE_STAT'],
  '<desde>':['SIMPLE_STAT'],
  '<log>':['SIMPLE_STAT'],
  '<retorno>':['SIMPLE_STAT'],
  '<token_integer>':['SIMPLE_STAT'],
  '<token_float>':['SIMPLE_STAT'],
  '<true>':['SIMPLE_STAT'],
  '<false>':['SIMPLE_STAT'],
  '<token_string>':['SIMPLE_STAT'],
  '<nil>':['SIMPLE_STAT'],
  '<token_cor_izq>':['SIMPLE_STAT'],
  '<token_llave_izq>':['SIMPLE_STAT'],
  '<if>':['COMP_STAT'],
  '<for>':['COMP_STAT'],
  '<while>':['COMP_STAT'],
  '<funcion>':['COMP_STAT'],
  '<token_menos>':['SIMPLE_STAT']
}

COMP_STAT={
  '<if>':['IF_STAT'],
  '<while>':['WHILE_STAT'],
  '<for>':['FOR_STAT'],
  '<funcion>':['FUN_STAT']
}

ATOM3={
  '<token_integer>':['<token_integer>'],
  '<token_float>':['<token_float>'],
  '<true>':['<true>'],
  '<false>':['<false>'],
  '<token_string>':['<token_string>'],
  '<token_cor_izq>':["ARRAY"],
  '<token_llave_izq>':["OBJETO"],
  '<nil>':['<nil>']
}

SIMPLE_STAT={
  '<id>':['ASSIGNMENT2'],
  '<log>':['LOG'],
  '<leer>':['LEER'],
  '<importar>':['IMPORTAR'],
  '<desde>':['IMPORTAR'],
  '<retorno>':['RETORNAR'],
  '<token_integer>':['ATOM3','SIMPLE_STATP'],
  '<token_float>':['ATOM3','SIMPLE_STATP'],
  '<true>':['ATOM3','SIMPLE_STATP'],
  '<false>':['ATOM3','SIMPLE_STATP'],
  '<token_string>':['ATOM3','SIMPLE_STATP'],
  '<nil>':['ATOM3','SIMPLE_STATP'],
  '<token_cor_izq>':['ATOM3','SIMPLE_STATP'],
  '<token_llave_izq>':['ATOM3','SIMPLE_STATP'],
  '<token_menos>':['<token_menos>','VARIABLE','SIMPLE_STATP']
}

SIMPLE_STATP={
  '<enter>':['<enter>'],
  '<token_mul>':['FACTOREXPR2'],
  '<token_div>':['FACTOREXPR2'],
  '<token_mod>':['FACTOREXPR2'],
  '<token_mas>':['FACTOREXPR2'],
  '<token_menos>':['FACTOREXPR2'],
  '<token_mayor_igual>':['FACTOREXPR2'],
  '<token_menor_igual>':['FACTOREXPR2'],
  '<token_mayor>':['FACTOREXPR2'],
  '<token_menor>':['FACTOREXPR2'],
  '<token_igual_num>':['FACTOREXPR2'],
  '<token_diff_num>':['FACTOREXPR2'],
  '<token_and>':['FACTOREXPR2'],
  '<token_or>':['FACTOREXPR2'],
  '<token_pot>':['FACTOREXPR2'],
  '<leer>':['FACTOREXPR2'],
  '<id>':['FACTOREXPR2'],
  '<importar>':['FACTOREXPR2'],
  '<desde>':['FACTOREXPR2'],
  '<log>':['FACTOREXPR2'],
  '<retorno>':['FACTOREXPR2'],
  '<if>':['FACTOREXPR2'],
  '<for>':['FACTOREXPR2'],
  '<while>':['FACTOREXPR2'],
  '<funcion>':['FACTOREXPR2'],
  '<token_assign>':['<token_assign>','ASSIGNMENTP'],
  '<EOF>':['<EOF>']
}

ASSIGNMENT={
  '<id>':['VARIABLE','<token_assign>','ASSIGNMENTP']
}

ASSIGNMENTP={
  '<token_not>':['EXPR'],
  '<token_par_izq>':['EXPR'],
  '<token_integer>':['EXPR'],
  '<token_float>':['EXPR'],
  '<true>':['EXPR'],
  '<false>':['EXPR'],
  '<token_string>':['EXPR'],
  '<nil>':['EXPR'],
  '<token_llave_izq>':['EXPR'],
  '<id>':['EXPR'],
  '<token_cor_izq>':['EXPR']
}

ASSIGNMENT2={
  '<id>':['<id>','ASSIGNMENT2P']
}

ASSIGNMENT2P={
  '<token_assign>':['<token_assign>','EXPR'],
  '<token_par_izq>':['<token_par_izq>','AUXV','<token_par_der>'],
  '<enter>':['epsilon'],
  '<EOF>':['epsilon'],
  '<id>':['epsilon'],
  '<importar>':['epsilon'],
  '<desde>':['epsilon'],
  '<leer>':['epsilon'],
  '<log>':['epsilon'],
  '<retorno>':['epsilon'],
  '<token_integer>':['epsilon'],
  '<token_float>':['epsilon'],
  '<true>':['epsilon'],
  '<false>':['epsilon'],
  '<token_string>':['epsilon'],
  '<nil>':['epsilon'],
  '<token_cor_izq>':['epsilon'],
  '<token_llave_izq>':['epsilon'],
  '<if>':['epsilon'],
  '<for>':['epsilon'],
  '<while>':['epsilon'],
  '<funcion>':['epsilon'],
  '<end>':['epsilon'],
  '<token_llave_der>':['epsilon'],
  '<token_point>':['<token_point>','ASSIGNMENT2P']
}

ASSIGNMENT3={
  '<id>':['<id>','ASSIGNMENT3P']
}

ASSIGNMENT3P={
  '<token_assign>':['<token_assign>','EXPR'],
  '<enter>':['epsilon']
}

IF_STAT={
  '<if>':['<if>','COND','ELSE_STAT']
}

ELSE_STAT={
  '<elif>':['<elif>','COND','ELSE_STAT'],
  '<else>':['<else>','STAT_BLOCK'],
  '<enter>':['<enter>','ELSE_STAT'],
  '<EOF>':['epsilon'],
  '<id>':['epsilon'],
  '<importar>':['epsilon'],
  '<desde>':['epsilon'],
  '<leer>':['epsilon'],
  '<log>':['epsilon'],
  '<retorno>':['epsilon'],
  '<token_integer>':['epsilon'],
  '<token_float>':['epsilon'],
  '<true>':['epsilon'],
  '<false>':['epsilon'],
  '<token_string>':['epsilon'],
  '<nil>':['epsilon'],
  '<token_cor_izq>':['epsilon'],
  '<token_llave_izq>':['epsilon'],
  '<if>':['epsilon'],
  '<for>':['epsilon'],
  '<while>':['epsilon'],
  '<funcion>':['epsilon'],
  '<end>':['epsilon'],
  '<token_llave_der>':['epsilon']
}

COND={
  '<token_par_izq>':['<token_par_izq>','EXPR','<token_par_der>','CONDP']
}

CONDP={
  '<token_llave_izq>':['STAT_BLOCK'],
  '<token_point>':['STAT_BLOCK'],
  '<id>':['STAT_BLOCK'],
  '<importar>':['STAT_BLOCK'],
  '<desde>':['STAT_BLOCK'],
  '<leer>':['STAT_BLOCK'],
  '<log>':['STAT_BLOCK'],
  '<token_integer>':['STAT_BLOCK'],
  '<token_float>':['STAT_BLOCK'],
  '<true>':['STAT_BLOCK'],
  '<false>':['STAT_BLOCK'],
  '<token_string>':['STAT_BLOCK'],
  '<nil>':['STAT_BLOCK'],
  '<token_cor_izq>':['STAT_BLOCK'],
  '<retorno>':['STAT_BLOCK'],
  '<if>':['STAT_BLOCK'],
  '<for>':['STAT_BLOCK'],
  '<while>':['STAT_BLOCK'],
  '<funcion>':['STAT_BLOCK'],
  '<enter>':['<enter>','STAT_BLOCK']
}

STAT_BLOCK={
  '<token_point>':['STAT2','<enter>'],
  '<id>':['STAT2','<enter>'],
  '<importar>':['STAT2','<enter>'],
  '<desde>':['STAT2','<enter>'],
  '<leer>':['STAT2','<enter>'],
  '<log>':['STAT2','<enter>'],
  '<token_integer>':['STAT2','<enter>'],
  '<token_float>':['STAT2','<enter>'],
  '<true>':['STAT2','<enter>'],
  '<false>':['STAT2','<enter>'],
  '<token_string>':['STAT2','<enter>'],
  '<nil>':['STAT2','<enter>'],
  '<token_cor_izq>':['STAT2','<enter>'],
  '<retorno>':['STAT2','<enter>'],
  '<if>':['STAT2','<enter>'],
  '<for>':['STAT2','<enter>'],
  '<while>':['STAT2','<enter>'],
  '<funcion>':['STAT2','<enter>'],
  '<enter>':['<enter>','STAT_BLOCK'],
  '<token_llave_izq>':['<token_llave_izq>','STAT_BLOCKP','<token_llave_der>']
}

STAT_BLOCKP={
  '<token_llave_der>':['epsilon'],
  '<enter>':['AUXF'],
  '<token_point>':['AUXF'],
  '<id>':['AUXF'],
  '<importar>':['AUXF'],
  '<desde>':['AUXF'],
  '<leer>':['AUXF'],
  '<log>':['AUXF'],
  '<retorno>':['AUXF'],
  '<token_integer>':['AUXF'],
  '<token_float>':['AUXF'],
  '<true>':['AUXF'],
  '<false>':['AUXF'],
  '<token_string>':['AUXF'],
  '<nil>':['AUXF'],
  '<token_cor_izq>':['AUXF'],
  '<token_llave_izq>':['AUXF'],
  '<if>':['AUXF'],
  '<for>':['AUXF'],
  '<while>':['AUXF'],
  '<funcion>':['AUXF']
}

STAT2={
  '<token_point>':['SIMPLE_STAT2'],
  '<id>':['SIMPLE_STAT2'],
  '<importar>':['SIMPLE_STAT2'],
  '<desde>':['SIMPLE_STAT2'],
  '<leer>':['SIMPLE_STAT2'],
  '<log>':['SIMPLE_STAT2'],
  '<token_integer>':['SIMPLE_STAT2'],
  '<token_float>':['SIMPLE_STAT2'],
  '<true>':['SIMPLE_STAT2'],
  '<false>':['SIMPLE_STAT2'],
  '<token_string>':['SIMPLE_STAT2'],
  '<nil>':['SIMPLE_STAT2'],
  '<token_cor_izq>':['SIMPLE_STAT2'],
  '<retorno>':['SIMPLE_STAT2'],
  '<if>':['COMP_STAT'],
  '<for>':['COMP_STAT'],
  '<while>':['COMP_STAT'],
  '<funcion>':['COMP_STAT']
}

SIMPLE_STAT2={
  '<id>':['ASSIGNMENT'],
  '<leer>':['LOG'],
  '<log>':['LOG'],
  '<importar>':['IMPORTAR'],
  '<desde>':['IMPORTAR'],
  '<retorno>':['RETORNAR'],
  '<token_integer>':['ATOM2','<enter>'],
  '<token_float>':['ATOM2','<enter>'],
  '<true>':['ATOM2','<enter>'],
  '<false>':['ATOM2','<enter>'],
  '<token_string>':['ATOM2','<enter>'],
  '<nil>':['ATOM2','<enter>'],
  '<token_cor_izq>':['ATOM2','<enter>']
}

ATOM2={
  '<token_integer>':['<token_integer>'],
  '<token_float>':['<token_float>'],
  '<true>':['<true>'],
  '<false>':['<false>'],
  '<token_string>':['<token_string>'],
  '<token_cor_izq>':["ARRAY"],
  '<nil>':['<nil>']
}

WHILE_STAT={
  '<while>':['<while>','EXPR','STAT_BLOCK']
}

FOR_STAT={
  '<for>':['<for>','<id>','<in>','EXPR','STAT_BLOCK']
}

OBJETO={
  '<token_llave_izq>':['<token_llave_izq>','AUXO','<token_llave_der>']
}

AUXO={
  '<id>':['KEYVALUE','AUXO'],
  '<token_coma>':['<token_coma>','KEYVALUE','AUXO'],
  '<token_llave_der>':['epsilon']
}

VARIABLE={
  '<id>':['<id>','AUXIP']
}

AUXIP={
  '<token_par_izq>':['<token_par_izq>','AUXV','<token_par_der>'],
  '<token_point>':['AUXI'],
  '<token_cor_izq>':['AUXI'],
  '<token_par_der>':['AUXI'],
  '<EOF>':['AUXI'],
  '<token_assign>':['AUXI'],
  '<token_mul>':['AUXI'],
  '<token_div>':['AUXI'],
  '<token_mod>':['AUXI'],
  '<token_mas>':['AUXI'],
  '<token_menos>':['AUXI'],
  '<token_mayor_igual>':['AUXI'],
  '<token_menor_igual>':['AUXI'],
  '<token_mayor>':['AUXI'],
  '<token_menor>':['AUXI'],
  '<token_igual_num>':['AUXI'],
  '<token_diff_num>':['AUXI'],
  '<token_and>':['AUXI'],
  '<token_or>':['AUXI'],
  '<token_coma>':['AUXI'],
  '<token_pot>':['AUXI'],
  '<token_not>':['AUXI'],
  #'<token_par_izq>':['AUXI'],
  '<token_integer>':['AUXI'],
  '<token_float>':['AUXI'],
  '<true>':['AUXI'],
  '<false>':['AUXI'],
  '<token_string>':['AUXI'],
  '<nil>':['AUXI'],
  '<token_llave_izq>':['AUXI'],
  '<id>':['AUXI'],
  '<token_cor_der>':['AUXI'],
  '<token_dosp>':['AUXI'],
  '<enter>':['AUXI'],
  '<funcion>':['AUXI'],
  '<leer>':['AUXI'],
  '<log>':['AUXI'],
  '<importar>':['AUXI'],
  '<desde>':['AUXI'],
  '<retorno>':['AUXI'],
  '<if>':['AUXI'],
  '<while>':['AUXI'],
  '<for>':['AUXI'],
  '<end>':['AUXI'],
  '<token_llave_der>':['AUXI']
}

AUXI={
  '<token_point>':['<token_point>','<id>','AUXI'],
  '<token_cor_izq>':['<token_cor_izq>','AUXV','<token_cor_der>'],
  '<token_assign>':['epsilon'],
  '<EOF>':['epsilon'],
  '<token_mul>':['epsilon'],
  '<token_div>':['epsilon'],
  '<token_mod>':['epsilon'],
  '<token_mas>':['epsilon'],
  '<token_menos>':['epsilon'],
  '<token_mayor_igual>':['epsilon'],
  '<token_menor_igual>':['epsilon'],
  '<token_mayor>':['epsilon'],
  '<token_menor>':['epsilon'],
  '<token_igual_num>':['epsilon'],
  '<token_diff_num>':['epsilon'],
  '<token_and>':['epsilon'],
  '<token_or>':['epsilon'],
  '<token_pot>':['epsilon'],
  '<enter>':['epsilon'],
  '<id>':['epsilon'],
  '<importar>':['epsilon'],
  '<desde>':['epsilon'],
  '<leer>':['epsilon'],
  '<log>':['epsilon'],
  '<retorno>':['epsilon'],
  '<token_integer>':['epsilon'],
  '<token_float>':['epsilon'],
  '<true>':['epsilon'],
  '<false>':['epsilon'],
  '<token_string>':['epsilon'],
  '<nil>':['epsilon'],
  '<token_llave_izq>':['epsilon'],
  '<if>':['epsilon'],
  '<for>':['epsilon'],
  '<while>':['epsilon'],
  '<funcion>':['epsilon'],
  '<end>':['epsilon'],
  '<token_llave_der>':['epsilon'],
  '<token_coma>':['epsilon'],
  '<token_not>':['epsilon'],
  '<token_par_izq>':['epsilon'],
  '<token_cor_der>':['epsilon'],
  '<token_par_der>':['epsilon'],
  '<token_dosp>':['epsilon']
}

IMPORTAR={
  '<importar>':['<importar>','<id>','AUXI'],
  '<desde>':['<desde>','<id>','<importar>','<id>']
}

LOG={
  '<log>':['<log>','<token_par_izq>','EXPR','<token_par_der>']
}

LEER={
  '<leer>':['<leer>','<token_par_izq>','VARIABLE','<token_par_der>']
}

RETORNAR={
  '<retorno>':['<retorno>','<token_par_izq>','EXPR','<token_par_der>','<enter>']
}

ACCESSARRAY={
  '<id>':['<id>','<token_cor_izq>','EXPR','<token_cor_der>']
}

AUXV={
  '<token_par_izq>':['EXPR','AUXVP'],
  '<token_not>':['EXPR','AUXVP'],
  '<token_integer>':['EXPR','AUXVP'],
  '<token_float>':['EXPR','AUXVP'],
  '<true>':['EXPR','AUXVP'],
  '<false>':['EXPR','AUXVP'],
  '<token_string>':['EXPR','AUXVP'],
  '<nil>':['EXPR','AUXVP'],
  '<token_cor_izq>':['EXPR','AUXVP'],
  '<id>':['EXPR','AUXVP'],
  '<token_llave_izq>':['EXPR','AUXVP'],
  '<token_mul>':['EXPR','AUXVP'],
  '<token_div>':['EXPR','AUXVP'],
  '<token_mod>':['EXPR','AUXVP'],
  '<token_mas>':['EXPR','AUXVP'],
  '<token_menos>':['EXPR','AUXVP'],
  '<token_mayor_igual>':['EXPR','AUXVP'],
  '<token_menor_igual>':['EXPR','AUXVP'],
  '<token_mayor>':['EXPR','AUXVP'],
  '<token_menor>':['EXPR','AUXVP'],
  '<token_igual_num>':['EXPR','AUXVP'],
  '<token_diff_num>':['EXPR','AUXVP'],
  '<token_and>':['EXPR','AUXVP'],
  '<token_or>':['EXPR','AUXVP'],
  '<token_pot>':['EXPR','AUXVP'],
  '<token_coma>':['EXPR','AUXVP'],
  '<token_cor_der>':['epsilon'],
  '<token_par_der>':['epsilon']
}

AUXVP={
  '<token_coma>':['<token_coma>','EXPR','AUXVP'],
  '<token_par_der>':['epsilon']
}

KEYVALUE={
  '<id>':['<id>','<token_dosp>','EXPR']
}

def checkLine(T,m):
  inicio=0
  last = 0
  k=0
  while(k <= len(T)):
    encontrado = checkRegex(T[inicio:k],m)
    #print(str(encontrado) + str(T[inicio:k]))
    #print(encontrado)
    if(((encontrado==0 or encontrado == "espacios") and (last != 0 and last != "espacios" and last != "completa"))):
      (darFormato(str(last),inicio,T[inicio:k-1],m))
      inicio = k-1
    elif(k==len(T) and encontrado=="espacios"):
      k+=1
    elif(k==len(T) and encontrado==0 and last == 0):
      (darFormato(str(encontrado),inicio,T[inicio:k],m))
      k+=1
    elif(k==len(T) and encontrado!=0):
      (darFormato(str(encontrado),inicio,T[inicio:k],m))
      k+=1
    elif(k==len(T) and encontrado==0 and last != 0):
      #print("holi")
      (darFormato(str(last),inicio,T[inicio:k-1],m))
      (darFormato(str(encontrado),k-1,T[k-1:k],m))
      k+=1
    elif(encontrado=="espacios"):
      inicio = k
    elif(encontrado=="completa"):
      darFormato(str(encontrado),inicio,T[inicio:k],m)
      inicio=k
      k += 1
    else:
      k += 1
    last=encontrado
  pos.append([m+1,k])

def darFormato(tipo, k, cadena,m):
  if(tipo == "t1"):
    pila.append("<"+diccionarioTokens[cadena]+">")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "t2"):
    pila.append("<"+diccionarioTokens[cadena]+">")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "tl"):
    pila.append("<"+cadena+">")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "identificador"):
    pila.append("<id>")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "flotante"):
    pila.append("<token_float>")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "entero"):
    pila.append("<token_integer>")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "comentario"):
    return("")
  elif(tipo == "incompleta"):
    print("Error lexico(linea:"+str(i+1)+",posicion:"+str(k+1)+")")
  elif(tipo == "completa"):
    pila.append("<token_string>")
    pos.append([m+1,k+1])
    content.append(cadena)
  elif(tipo == "0"):
    print(">>> Error lexico(linea:"+str(i+1)+",posicion:"+str(k+1)+")")
    sys.exit()

def checkRegex(T,m):
  if(re.search(comentario,T)):
    return("comentario")
  elif(re.search(stringCompleta,T)):
    return("completa")
  elif(re.search(stringIncompleta,T)):
    return("incompleta")
  elif(re.search(tokensreservados1,T)):
    return("t1")
  elif(re.search(tokensreservados2,T)):
    return("t2")
  elif(re.search(tokensLargos,T)):
    return("tl")
  elif(re.search(identificador,T)):
    return("identificador")
  elif(re.search(flotante,T)):
    return("flotante")
  elif(re.search(entero,T)):
    return("entero")
  elif(re.search(espacios,T)):
    return("espacios")
  else:
    return(0)

i=0

def analizar(diccionario):
  global i
  if(i>=len(pila) or (diccionario=="<EOF>" and pila[i]=="<EOF>")):
    print("El analisis sintactico ha finalizado correctamente.")
    sys.exit()
  #print("\n"+diccionario)
  #print(pila[i])
  if(diccionario==pila[i]):
    i=i+1
  elif(diccionario=="FROM_FILE"):
    if(pila[i] in FROM_FILE):
      thisindex=i
      for r in range(len(FROM_FILE[pila[i]])):
        #print("ffile[tok] " + str(FROM_FILE[pila[thisindex]]))
        analizar(FROM_FILE[pila[thisindex]][r])
  elif(diccionario=="STAT"):
    if(pila[i] in STAT):
      thisindex=i
      for r in range(len(STAT[pila[i]])):
        #print("STAT[tok] " + str(STAT[pila[thisindex]]))
        analizar(STAT[pila[thisindex]][r])
  elif(diccionario=="COMP_STAT"):
    if(pila[i] in COMP_STAT):
      thisindex=i
      for r in range(len(COMP_STAT[pila[i]])):
        #print("COMP_STAT[tok] " + str(COMP_STAT[pila[thisindex]]))
        analizar(COMP_STAT[pila[thisindex]][r])
  elif(diccionario=="IF_STAT"):
    if(pila[i] in IF_STAT):
      thisindex=i
      for r in range(len(IF_STAT[pila[i]])):
        #print("IF_STAT[tok] " + str(IF_STAT[pila[thisindex]]))
        analizar(IF_STAT[pila[thisindex]][r])
  elif(diccionario=="COND"):
    if(pila[i] in COND):
      thisindex=i
      for r in range(len(COND[pila[i]])):
        #print("COND[tok] " + str(COND[pila[thisindex]]))
        analizar(COND[pila[thisindex]][r])
    else:
      if(pila[i]=='<enter>'):
        i=i+1
      toprint=""
      for key, value in COND.items():
        toprint= key
      print("<"+str(pos[i][0])+":"+str(pos[i][1])+"> Error sintactico. Encontrado: '"+content[i]+"'; se esperaba: '"+buscar(toprint)+"'.")
      sys.exit()
      sys.exit()
  elif(diccionario=="EXPR"):
    if(pila[i] in EXPR):
      thisindex=i
      for r in range(len(EXPR[pila[i]])):
        #print("EXPR[tok] " + str(EXPR[pila[thisindex]]))
        analizar(EXPR[pila[thisindex]][r])
    else:
        if(pila[i]=='<enter>'):
            i=i+1
        print("<"+str(pos[i][0])+":"+str(pos[i][1])+"> Error sintactico. Encontrado: '"+content[i]+"'; se esperaba: ",end="")
        Lista=[]
        for key, value in EXPR.items():
            Lista.append(buscar(key))
        Lista.sort()
        for s in range(len(Lista)):
            if(Lista[s]=="id"):
                Lista[s]="identificador"
            if(s!=len(Lista)-1):
                print("'"+Lista[s]+"', ",end="")
            else:
                print("'"+Lista[s]+"'",end="")
        print(".",end="")
            
        sys.exit()
  elif(diccionario=="EXPR2"):
    if(pila[i] in EXPR2):
      thisindex=i
      for r in range(len(EXPR2[pila[i]])):
        #print("EXPR2[tok] " + str(EXPR2[pila[thisindex]]))
        analizar(EXPR2[pila[thisindex]][r])
  elif(diccionario=="ATOM"):
    if(pila[i] in ATOM):
      thisindex=i
      for r in range(len(ATOM[pila[i]])):
        #print("ATOM[tok] " + str(ATOM[pila[thisindex]]))
        analizar(ATOM[pila[thisindex]][r])
  elif(diccionario=="VARIABLE"):
    if(pila[i] in VARIABLE):
      thisindex=i
      for r in range(len(VARIABLE[pila[i]])):
        #print("VARIABLE[tok] " + str(VARIABLE[pila[thisindex]]))
        analizar(VARIABLE[pila[thisindex]][r])
  elif(diccionario=="AUXIP"):
    if(pila[i] in AUXIP):
      thisindex=i
      for r in range(len(AUXIP[pila[i]])):
        #print("AUXIP[tok] " + str(AUXIP[pila[thisindex]]))
        analizar(AUXIP[pila[thisindex]][r])
  elif(diccionario=="AUXI"):
    if(pila[i] in AUXI):
      thisindex=i
      for r in range(len(AUXI[pila[i]])):
        #print("AUXI[tok] " + str(AUXI[pila[thisindex]]))
        analizar(AUXI[pila[thisindex]][r])
  elif(diccionario=="FACTOREXPR2"):
    if(pila[i] in FACTOREXPR2):
      thisindex=i
      for r in range(len(FACTOREXPR2[pila[i]])):
        #print("FACTOREXPR2[tok] " + str(FACTOREXPR2[pila[thisindex]]))
        analizar(FACTOREXPR2[pila[thisindex]][r])
  elif(diccionario=="CONDP"):
    if(pila[i] in CONDP):
      thisindex=i
      for r in range(len(CONDP[pila[i]])):
        #print("CONDP[tok] " + str(CONDP[pila[thisindex]]))
        analizar(CONDP[pila[thisindex]][r])
  elif(diccionario=="STAT_BLOCK"):
    if(pila[i] in STAT_BLOCK):
      thisindex=i
      for r in range(len(STAT_BLOCK[pila[i]])):
        #print("STAT_BLOCK[tok] " + str(STAT_BLOCK[pila[thisindex]]))
        analizar(STAT_BLOCK[pila[thisindex]][r])
  elif(diccionario=="STAT_BLOCKP"):
    if(pila[i] in STAT_BLOCKP):
      thisindex=i
      for r in range(len(STAT_BLOCKP[pila[i]])):
        #print("STAT_BLOCKP[tok] " + str(STAT_BLOCKP[pila[thisindex]]))
        analizar(STAT_BLOCKP[pila[thisindex]][r])
  elif(diccionario=="AUXF"):
    if(pila[i] in AUXF):
      thisindex=i
      for r in range(len(AUXF[pila[i]])):
        #print("AUXF[tok] " + str(AUXF[pila[thisindex]]))
        analizar(AUXF[pila[thisindex]][r])
  elif(diccionario=="SIMPLE_STAT"):
    if(pila[i] in SIMPLE_STAT):
      thisindex=i
      for r in range(len(SIMPLE_STAT[pila[i]])):
        #print("SIMPLE_STAT[tok] " + str(SIMPLE_STAT[pila[thisindex]]))
        analizar(SIMPLE_STAT[pila[thisindex]][r])
  elif(diccionario=="LOG"):
    if(pila[i] in LOG):
      thisindex=i
      for r in range(len(LOG[pila[i]])):
        #print("LOG[tok] " + str(LOG[pila[thisindex]]))
        analizar(LOG[pila[thisindex]][r])
  elif(diccionario=="ELSE_STAT"):
    if(pila[i] in ELSE_STAT):
      thisindex=i
      for r in range(len(ELSE_STAT[pila[i]])):
        #print("ELSE_STAT[tok] " + str(ELSE_STAT[pila[thisindex]]))
        analizar(ELSE_STAT[pila[thisindex]][r])
  elif(diccionario=="ATOM3"):
    if(pila[i] in ATOM3):
      thisindex=i
      for r in range(len(ATOM3[pila[i]])):
        #print("ATOM3[tok] " + str(ATOM3[pila[thisindex]]))
        analizar(ATOM3[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENT3"):
    if(pila[i] in ASSIGNMENT3):
      thisindex=i
      for r in range(len(ASSIGNMENT3[pila[i]])):
        #print("ASSIGNMENT3[tok] " + str(ASSIGNMENT3[pila[thisindex]]))
        analizar(ASSIGNMENT3[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENT2"):
    if(pila[i] in ASSIGNMENT2):
      thisindex=i
      for r in range(len(ASSIGNMENT2[pila[i]])):
        #print("ASSIGNMENT2[tok] " + str(ASSIGNMENT2[pila[thisindex]]))
        analizar(ASSIGNMENT2[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENT2P"):
    if(pila[i] in ASSIGNMENT2P):
      thisindex=i
      for r in range(len(ASSIGNMENT2P[pila[i]])):
        #print("ASSIGNMENT2P[tok] " + str(ASSIGNMENT2P[pila[thisindex]]))
        analizar(ASSIGNMENT2P[pila[thisindex]][r])
  elif(diccionario=="FOR_STAT"):
    if(pila[i] in FOR_STAT):
      thisindex=i
      for r in range(len(FOR_STAT[pila[i]])):
        #print("FOR_STAT[tok] " + str(FOR_STAT[pila[thisindex]]))
        analizar(FOR_STAT[pila[thisindex]][r])
  elif(diccionario=="ARRAY"):
    if(pila[i] in ARRAY):
      thisindex=i
      for r in range(len(ARRAY[pila[i]])):
        #print("ARRAY[tok] " + str(ARRAY[pila[thisindex]]))
        analizar(ARRAY[pila[thisindex]][r])
  elif(diccionario=="INTERNARRAY"):
    if(pila[i] in INTERNARRAY):
      thisindex=i
      for r in range(len(INTERNARRAY[pila[i]])):
        #print("INTERNARRAY[tok] " + str(INTERNARRAY[pila[thisindex]]))
        analizar(INTERNARRAY[pila[thisindex]][r])
  elif(diccionario=="INTERNARRAYP"):
    if(pila[i] in INTERNARRAYP):
      thisindex=i
      for r in range(len(INTERNARRAYP[pila[i]])):
        #print("INTERNARRAYP[tok] " + str(INTERNARRAYP[pila[thisindex]]))
        analizar(INTERNARRAYP[pila[thisindex]][r])
  elif(diccionario=="INTERNARRAY1"):
    if(pila[i] in INTERNARRAY1):
      thisindex=i
      for r in range(len(INTERNARRAY1[pila[i]])):
        #print("INTERNARRAY1[tok] " + str(INTERNARRAY1[pila[thisindex]]))
        analizar(INTERNARRAY1[pila[thisindex]][r])
  elif(diccionario=="OBJETO"):
    if(pila[i] in OBJETO):
      thisindex=i
      for r in range(len(OBJETO[pila[i]])):
        #print("OBJETO[tok] " + str(OBJETO[pila[thisindex]]))
        analizar(OBJETO[pila[thisindex]][r])
  elif(diccionario=="AUXO"):
    if(pila[i] in AUXO):
      thisindex=i
      for r in range(len(AUXO[pila[i]])):
        #print("AUXO[tok] " + str(AUXO[pila[thisindex]]))
        analizar(AUXO[pila[thisindex]][r])
  elif(diccionario=="KEYVALUE"):
    if(pila[i] in KEYVALUE):
      thisindex=i
      for r in range(len(KEYVALUE[pila[i]])):
        #print("KEYVALUE[tok] " + str(KEYVALUE[pila[thisindex]]))
        analizar(KEYVALUE[pila[thisindex]][r])
  elif(diccionario=="FUN_STAT"):
    if(pila[i] in FUN_STAT):
      thisindex=i
      for r in range(len(FUN_STAT[pila[i]])):
        #print("FUN_STAT[tok] " + str(FUN_STAT[pila[thisindex]]))
        analizar(FUN_STAT[pila[thisindex]][r])
  elif(diccionario=="AUXV"):
    if(pila[i] in AUXV):
      thisindex=i
      for r in range(len(AUXV[pila[i]])):
        #print("AUXV[tok] " + str(AUXV[pila[thisindex]]))
        analizar(AUXV[pila[thisindex]][r])
  elif(diccionario=="AUXP"):
    if(pila[i] in AUXP):
      thisindex=i
      for r in range(len(AUXP[pila[i]])):
        #print("AUXP[tok] " + str(AUXP[pila[thisindex]]))
        analizar(AUXP[pila[thisindex]][r])
  elif(diccionario=="PARAM"):
    if(pila[i] in PARAM):
      thisindex=i
      for r in range(len(PARAM[pila[i]])):
        #print("PARAM[tok] " + str(PARAM[pila[thisindex]]))
        analizar(PARAM[pila[thisindex]][r])
  elif(diccionario=="FACTORAUXP"):
    if(pila[i] in FACTORAUXP):
      thisindex=i
      for r in range(len(FACTORAUXP[pila[i]])):
        #print("FACTORAUXP[tok] " + str(FACTORAUXP[pila[thisindex]]))
        analizar(FACTORAUXP[pila[thisindex]][r])
  elif(diccionario=="RETORNAR"):
    if(pila[i] in RETORNAR):
      thisindex=i
      for r in range(len(RETORNAR[pila[i]])):
        #print("RETORNAR[tok] " + str(RETORNAR[pila[thisindex]]))
        analizar(RETORNAR[pila[thisindex]][r])
  elif(diccionario=="AUXVP"):
    if(pila[i] in AUXVP):
      thisindex=i
      for r in range(len(AUXVP[pila[i]])):
        #print("AUXVP[tok] " + str(AUXVP[pila[thisindex]]))
        analizar(AUXVP[pila[thisindex]][r])
  elif(diccionario=="EXPRCOMA"):
    if(pila[i] in EXPRCOMA):
      thisindex=i
      for r in range(len(EXPRCOMA[pila[i]])):
        #print("EXPRCOMA[tok] " + str(EXPRCOMA[pila[thisindex]]))
        analizar(EXPRCOMA[pila[thisindex]][r])
  elif(diccionario=="STAT2"):
    if(pila[i] in STAT2):
      thisindex=i
      for r in range(len(STAT2[pila[i]])):
        #print("STAT2[tok] " + str(STAT2[pila[thisindex]]))
        analizar(STAT2[pila[thisindex]][r])
  elif(diccionario=="SIMPLE_STAT2"):
    if(pila[i] in SIMPLE_STAT2):
      thisindex=i
      for r in range(len(SIMPLE_STAT2[pila[i]])):
        #print("SIMPLE_STAT2[tok] " + str(SIMPLE_STAT2[pila[thisindex]]))
        analizar(SIMPLE_STAT2[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENT3P"):
    if(pila[i] in ASSIGNMENT3P):
      thisindex=i
      for r in range(len(ASSIGNMENT3P[pila[i]])):
        #print("ASSIGNMENT3P[tok] " + str(ASSIGNMENT3P[pila[thisindex]]))
        analizar(ASSIGNMENT3P[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENT"):
    if(pila[i] in ASSIGNMENT):
      thisindex=i
      for r in range(len(ASSIGNMENT[pila[i]])):
        #print("ASSIGNMENT[tok] " + str(ASSIGNMENT[pila[thisindex]]))
        analizar(ASSIGNMENT[pila[thisindex]][r])
  elif(diccionario=="ASSIGNMENTP"):
    if(pila[i] in ASSIGNMENTP):
      thisindex=i
      for r in range(len(ASSIGNMENTP[pila[i]])):
        #print("ASSIGNMENTP[tok] " + str(ASSIGNMENTP[pila[thisindex]]))
        analizar(ASSIGNMENTP[pila[thisindex]][r])
  elif(diccionario=="LEER"):
    if(pila[i] in LEER):
      thisindex=i
      for r in range(len(LEER[pila[i]])):
        #print("LEER[tok] " + str(LEER[pila[thisindex]]))
        analizar(LEER[pila[thisindex]][r])
  elif(diccionario=="WHILE_STAT"):
    if(pila[i] in WHILE_STAT):
      thisindex=i
      for r in range(len(WHILE_STAT[pila[i]])):
        #print("WHILE_STAT[tok] " + str(WHILE_STAT[pila[thisindex]]))
        analizar(WHILE_STAT[pila[thisindex]][r])
  elif(diccionario=="FACTORPARAM"):
    if(pila[i] in FACTORPARAM):
      thisindex=i
      for r in range(len(FACTORPARAM[pila[i]])):
        #print("FACTORPARAM[tok] " + str(FACTORPARAM[pila[thisindex]]))
        analizar(FACTORPARAM[pila[thisindex]][r])
  elif(diccionario=="SIMPLE_STATP"):
    if(pila[i] in SIMPLE_STATP):
      thisindex=i
      for r in range(len(SIMPLE_STATP[pila[i]])):
        #print("SIMPLE_STATP[tok] " + str(SIMPLE_STATP[pila[thisindex]]))
        analizar(SIMPLE_STATP[pila[thisindex]][r])
  elif(diccionario=="IMPORTAR"):
    if(pila[i] in IMPORTAR):
      thisindex=i
      for r in range(len(IMPORTAR[pila[i]])):
        #print("IMPORTAR[tok] " + str(IMPORTAR[pila[thisindex]]))
        analizar(IMPORTAR[pila[thisindex]][r])
  elif(diccionario=="DESDE"):
    if(pila[i] in DESDE):
      thisindex=i
      for r in range(len(DESDE[pila[i]])):
        #print("DESDE[tok] " + str(DESDE[pila[thisindex]]))
        analizar(DESDE[pila[thisindex]][r])
        
  elif(diccionario!="epsilon"):
    if(pila[i]=='<enter>'):
      i=i+1
    print("<"+str(pos[i][0])+":"+str(pos[i][1])+"> Error sintactico. Encontrado: '"+content[i]+"'; se esperaba: '"+buscar(diccionario)+"'.")
    sys.exit()
        

def buscar(result):
  toret=result[1:-1]
  for key, val in diccionarioTokens.items():    
    if val == result[1:-1]:
      toret=key
      return(toret)
  return(toret)


#Entrada= open("archivo.txt", "r")
'''
while(True):
    try:
        lines = input()
        print(pila)
    except EOFError:
        print("\n")
        sys.exit()
    for m in range(0, len(lines)):
      if(len(lines[m][:-1])>=1):
        checkLine(lines[m][:-1],m)
      else:
        pos.append([m+1,1])
      pila.append("<enter>")
      content.append("\n")
    pila.append("<EOF>")

for cs in range(len(content)):
  print(pos[cs])
  print(content[cs])
  print("\n")

if(pila[0] in SOURCE):
   analizar(SOURCE[pila[0]][0])
'''   



m=0
while(True):
    try:
        lines = input()
        #print(pila)
        #print("lines" + lines)
    except EOFError:
        #print("\n")
        break
    if(len(lines)>=1):
        checkLine(lines,m)
    else:
        pos.append([m+1,1])
    pila.append("<enter>")
    content.append("\n")
    m+=1
pila.append("<EOF>")

if(pila[0] in SOURCE):
   analizar(SOURCE[pila[0]][0])

#Entrada.close()

