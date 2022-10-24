# Functions

#-------------------------------------------------------------------------------------------------------------------------

def fetchMissing(a, b):
    '''This functions receives two pokemon id numbers as integers ('a' and 'b'),
    and returns a dataframe containing the specified pokemon from the ids 'a' to 'b'.
    '''
    missing_pokes = []
    for i in range(a,b+1):
        time.sleep(1)
        print(f"Fetching pokemon with id: {i}")
        response_api = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}/").json()
        missing_pokes.append(response_api)
    
    return json_normalize(missing_pokes)

#-------------------------------------------------------------------------------------------------------------------------

def extractStats(df):
    '''This function receives a dataframe and extracts the HP, Attack, Defense, Sp. Atk, Sp. Def, and Speed from 'stats'.
    It returns a df with the extracted values of each stat for each pokemon in new columns.
    '''
    HP = []
    Attack = []
    Defense = []
    Sp_Atk = []
    Sp_Def = []
    Speed = []
    
    for i in range(len(df)):
        HP.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[0] if x.isdigit()])))
        Attack.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[4] if x.isdigit()])))
        Defense.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[8] if x.isdigit()])))
        Sp_Atk.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[12] if x.isdigit()])))
        Sp_Def.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[16] if x.isdigit()])))
        Speed.append(int("".join([x for x in df.iloc[i]['stats'].split(",")[20] if x.isdigit()])))
    
    df['HP'] = HP
    df['Attack'] = Attack
    df['Defense'] = Defense
    df['Sp. Atk'] = Sp_Atk
    df['Sp. Def'] = Sp_Def
    df['Speed'] = Speed
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def cleanColumns(df):
    '''This functions receives a dataframe and drops unwanted columns from the dataframe.
    '''
    df = df.drop(labels=list(df.filter(regex='sprites.*')), axis=1)
    df = df.drop(labels=['game_indices', 
                         'held_items', 
                         'is_default', 
                         'past_types', 
                         'species.name', 
                         'species.url', 
                         'order', 
                         'forms', 
                         'abilities', 
                         'base_experience', 
                         'location_area_encounters', 
                         'moves',
                         'stats', 
                         'types'], axis=1)
    df.columns = df.columns.str.title()
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def transformMetrics(df):
    '''This function receives a dataframe and transforms heights and weights to meters and kilograms, respectively.
    '''
    df['Height'] = df['Height'].apply(lambda x: x / 10)
    df['Weight'] = df['Weight'].apply(lambda x: x / 10)
    return df

#-------------------------------------------------------------------------------------------------------------------------

def calculateTotal(df):
    '''This function receives a dataframe and calculates the Total score of a pokemon
    based on the sum of its stats (Hp, Attack, Defense, Sp. Atk, Sp. Def, Speed).
    It returns the dataframe with the Total column.
    '''
    df['Total'] = df['Hp'] + df['Attack'] + df['Defense'] + df['Sp. Atk'] + df['Sp. Def'] + df['Speed']
    return df

#-------------------------------------------------------------------------------------------------------------------------

def setGeneration(df):
    '''This function receives a dataframe and returns the generation to which the pokemon belongs based on its ID.
    '''
    generation_7 = [n for n in range(722,810)]
    generation_8 = [n for n in range(810,905)]
    
    df['Generation'] = df['Id'].apply(lambda x: 7 if x in generation_7 else 8)
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def setLegendary(df):
    '''This function receives a dataframe and returns the legendary status (True/False) of a pokemon based on its ID.
    '''
    gen_7_legendaries = [772,773,785,786,787,788,789,790,791,792,793,800] 
    gen_8_legendaries = [888,889,890,891,892,894,895,896,897,898,905]
    legendaries = gen_7_legendaries + gen_8_legendaries
    
    df['Legendary'] = df['Id'].apply(lambda x: True if x in legendaries else False)
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def cleanNames(df):
    '''This function receives a dataframe and cleans the Name column.
    '''
    for i in df['Name']:
        if "-" in i:
            df['Name'] = df['Name'].str.replace(i, i.split("-")[0])
    df['Name'] = df['Name'].str.title()
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def nameChange(df):
    '''This function receives a dataframe and updates the name of some pokemon.
    '''
    names_change = {'Type' : 'Codigo_Cero',
               'Jangmo' : 'Jangmo-o',
               'Hakamo' : 'Hakamo-o',
               'Kommo' : 'Kommo-o',
               'Mr' : 'Mr._Rime'}
    
    df['Name'] = df['Name'].replace(names_change)
    df.loc[df['Id'] == 785, 'Name'] = "Tapu_Koko"
    df.loc[df['Id'] == 786, 'Name'] = "Tapu_Lele"
    df.loc[df['Id'] == 787, 'Name'] = "Tapu_Bulu"
    df.loc[df['Id'] == 788, 'Name'] = "Tapu_Fini"
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

# After applying this function you will need to append the types_list as a new column of the dataframe.

def getType(list_of_pokes):
    '''This functions appends the Type of each pokemon to a list.
    If the pokemon is not found in the wiki, it appends "NaN" instead.
    '''
    types_list = []
    
    for i in range(len(list_of_pokes)):
        pokemon_url = f"https://www.wikidex.net/wiki/{list_of_pokes[i]}"
        response = requests.get(pokemon_url)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        types = soup.find("p")
        try:
            types_list.append(types.getText().split("tipo ")[1].split(" ")[0])
        except IndexError:
            types_list.append('NaN')
        
    return types_list

#-------------------------------------------------------------------------------------------------------------------------

def cleanTypes(df):
    '''This function receives a dataframe, splits the column Type and translates the content, from ES to EN.
    '''
    df[["Type 1", "Type 2"]] = df["Types"].str.split("/", 1, expand = True)
    df = df.drop(labels="Types", axis=1)
    
    translate = {"normal" : "Normal",
                 "fuego" : "Fire",
                 "agua" : "Water",
                 "planta" : "Grass",
                 "volador" : "Flying",
                 "tierra" : "Ground",
                 "roca" : "Rock",
                 "eléctrico" : "Electric",
                 "bicho" : "Bug",
                 "lucha" : "Fighting",
                 "psíquico" : "Psychic",
                 "veneno" : "Poison",
                 "fantasma" : "Ghost",
                 "hielo" : "Ice",
                 "dragón" : "Dragon",
                 "acero" : "Steel",
                 "siniestro" : "Dark",
                 "hada" : "Fairy"}
        
    df['Type 1'] = df['Type 1'].replace(translate)
    df['Type 2'] = df['Type 2'].replace(translate)
    
    return df

#-------------------------------------------------------------------------------------------------------------------------

def organizeMissing(df):
    '''This function re-organizes the columns to match the original pokemon dataset from kaggle.
    '''
    df = df.rename(columns = {"Weight" : "Weight (kg)", "Height" : "Height (m)", "Id" : "#", "Hp" : "HP"})
    df = df.reindex(columns = ["#", "Name", "Type 1", "Type 2", "Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Generation", "Legendary", "Weight (kg)", "Height (m)"])

    return df

#-------------------------------------------------------------------------------------------------------------------------

# After applying this function you will need to append the weight_list as a new column of the dataframe.

def getWeight(list_of_pokes):
    '''This functions appends the weight of each pokemon to a list.
    If the pokemon is not found in the wiki, it appends "NaN" instead.
    '''
    weight_list = []
    
    for i in range(len(list_of_pokes)):
        pokemon_url = f"https://www.wikidex.net/wiki/{list_of_pokes[i]}"
        response = requests.get(pokemon_url)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        weight = soup.find_all("tr", attrs = {"title" : "Peso del Pokémon"})
        
        try:
            weight_float = float(weight[0].getText().strip().split('\n')[-1].split(" ")[0].replace(",","."))
            weight_list.append(weight_float)
        except IndexError:
            weight_list.append('NaN')
        
    return weight_list

#-------------------------------------------------------------------------------------------------------------------------

# After applying this function you will need to append the height_list as a new column of the dataframe.

def getHeight(list_of_pokes):
    '''This functions appends the height of each pokemon to a list.
    If the pokemon is not found in the wiki, it appends "NaN" instead.
    '''
    height_list = []
    
    for i in range(len(list_of_pokes)):
        pokemon_url = f"https://www.wikidex.net/wiki/{list_of_pokes[i]}"
        response = requests.get(pokemon_url)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        height = soup.find_all("tr", attrs = {"title" : "Altura del Pokémon"})
        
        try:
            height_float = float(height[0].getText().strip().split('\n')[-1].split(" ")[0].replace(",","."))
            height_list.append(height_float)
        except IndexError:
            height_list.append('NaN')
        
    return height_list

#-------------------------------------------------------------------------------------------------------------------------

# After applying this function you will need to append the catch_list as a new column of the dataframe.

def getCatchrate(list_of_pokes):
    '''This functions appends the Catch rate of each pokemon to a list.
    If the pokemon is not found in the wiki, it appends "NaN" instead.
    '''
    catch_list = []
    
    for i in range(len(list_of_pokes)):
        pokemon_url = f"https://www.wikidex.net/wiki/{list_of_pokes[i]}"
        response = requests.get(pokemon_url)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        catch = soup.find_all("ul")
        try:
            catch_list.append(int(re.search(r'\d+', str(catch).split("Ratio de captura</a>: ")[1]).group()))
        except IndexError:
            catch_list.append('NaN')
        
    return catch_list

#-------------------------------------------------------------------------------------------------------------------------

def reorganize(df):
    '''This function receives a df and reorganizes the columns as indicated.
    '''
    df = df.reindex(columns = ["#", "Name", "Weight (kg)", "Height (m)", "Type 1", "Type 2", "Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Catch rate","Generation", "Legendary"])

#-------------------------------------------------------------------------------------------------------------------------
