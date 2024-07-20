![alt text](<assets/header.png?raw=true>)

# EHRudite

EHRudite was a Retrieval-Augmented Generation (RAG) English-to-MySQL translation tool developed by Isaac Song, Anthony Zang, Zini Chakraborty, and Michael Edoigiawerie from the Georgia Institute of Technology during the 2024 36-hour Hacklytics Hackathon hosted @ Georgia Tech (February 9th – February 11th, 2024).

## Our Goal

As a team, we aimed to create a tool to bridge the gap between natural language and SQL, the average user and complex databases of essential medical data. Our name, EHRudite, derives from the standard acronym for `Electronic Health Records (EHR)` and the formal definition of ehrudite as a term, one describing the expertise and advancement that many medical professionals stand to represent and share.

## Datasets
### MIMIC-III
To begin testing and developing our work, we made use of the `MIMIC-III Clinical Database`, a publically avalible dataset anonymized dataset of over 40,000 patients ranging from long-term stay patients to ICU cases. This gave us a sizable dataset to act on. Though we initially hoped to gaina access to newer MIMIC-IV datasets, we were unable due to the approval and credential process associated.


### EHR-SQL
An existing initiative based on `MIMIC-III` had previously attempted manually translating ~200 English requests by hospital staff including physicians, nurses, health record teams, and others into verified SQLite queries. We were able to leverage this pretranslated data to implement our RAG system.


### Synthetic Datasets
Despite the lack of MIMIC-IV access, we were able to leverage the existing MIMIC-III data to propogate additional interally-consistent test cases, greatly expanding the scale of our resources for additional rapid testing. All generated data was confirmed to be integrity maintaining in context of the SQL constraints we identified and applied to the end MySQL server.


### MySQL and Hosting
We identified the constraints and propogation method used on the MIMIC-III dataset and automated the process of constructing a **fully-constrained** MySQL databse from the provided `.csv` sourcefiles for querying and ease of use. Once convertedwe selected `PlanetScale` as our hosting platform management and access of our over `250k` entries across multiple tables. This yielded a reliable and easily scalable platform for future development.

This ultimately allows for the most realistic testing (non-physicians/reasearchers) could afford given our resources.


## What Sets us Apart: Our Pipeline</b>
Our system incorporated a 3-part process to generate the most accurate result possible for the user.

<table border="0">
 <tr>
    <td valign="top">
        <h3>1. Sentence Transformers Precomputation Curration</h3> 
        Sentence transformers are used to identify the 10-20 most similar English statements from the EHR-SQL dataset. This helps us currate a selection of relevant precomputed question queries that we can pass alongside our primary query to achieve drastically improved accuracy and consistency.
        </br>
        </br>
        This is...
        </br>
        - Fast due to pre-computation
        </br>
        - Cheap
        </br>
        - Accurate
        </br>
        - Perfect for limited scopes such as EHRs
    </td>
    <td><img src="assets/pipline process.png?raw=true" alt="EHRudite RAG process pipline developed by students at Georgia Tech for a 36 hour hackathon" width="2200"></td>
 </tr>
</table>


<h3>2. RAG with OpenAI GPT4.o</h3>

The original user request and database schema are passed through the OpenAI `GPT4.o` to attempt to generate a valid MySQL query. The 10-20 identiifed precomputed SQL statements are passed alongside as a RAG input to assist in currating a more narrow response.


<h3>3. Repetition Loop and Testing</h3>
Because of the characteristic of generative AI having the potential to give slightly to drastically differing outputs each iteration, we're able to fact-check and self-correct each result we gain.

</br>

During this phase, we take the returned MySQL query, test it on our database, and check for the output. The result will be one of a valid correct query, valid but incorrect query, or a query that goes against the constraints and design of our SQL server. 

</br>

We then take this result and provide it as feedback to the `GPT` query to assist in revising the original output, iterating multiple times until we receive a sufficiently validated response of which we output to the user.


## Our Interface

Given the timeconstraints, our interface was simplistic and to the point. We made use of MongoDB, Node, React, Flask, and other tools to give us a point of entry to request english queries.

![EHRudite Input query example for what a medical practioner may ask](assets/query_example.png?raw=true)

> Figure 2. A screenshot of our input screen and a potential question a medical practioner may request from our system.

![EHRudite front page sample displaying the most recent requests, most recent returned result, and the data affiliated](assets/query_example_2.png?raw=true)

> Figure 3. A screenshot of our homepage displaying the following:
>
> - Enter Text: The input location as seen in figure 1.
>
> - SELECT query: the MySQL query returned by our pipeline that was used to retrive the information from our PlanetScale server.
>
> - The data retrieved by our query in a plaintext format
>
> - Most Recent Responses: Requests the user has recently queried our pipeline

![EHRudite the selected 10-20 similar precomputed statements selected](assets/query_output.png?raw=true)

> Figure 4. The 10-20 statements identified by our sentence transformers to be similar that were used to assist in our RAG pipeline.

## Future Development Plans
- Higher-powered LLM
- More developed UI
- Improved feedback loop
- Graphical displays for outputs and data
- User permissions
- More databases (including those of different formats and standards)