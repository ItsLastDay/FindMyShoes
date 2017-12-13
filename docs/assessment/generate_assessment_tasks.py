import glob
import re
import random

tasks = [] # [ (query, docs) ] 

for f in glob.glob('../../data/assessment_tasks/*.html'):
    fname = f[f.rindex('/')+1:f.rindex('.')]

    docs = []
    with open(f, 'r') as inp:
        text = inp.read()
        
        for doc in re.findall('a href="(.*?)"', text):
            docs.append(doc)

    tasks.append((fname, docs))


all_tasks = []

# 3 assessor judgements for each query.
for i in range(3):
    for task in tasks:
        all_tasks.append(task)


for person in ['Mike', 'Andrey', 'Ivan', 'Vlad', 'Anya']:
    tasks_for_this_person = set()
    with open('./assessment_{}.md'.format(person), 'w') as person_task:
        print('## Задание для {}\n'.format(person), file=person_task)
        print('Спасибо, что участвуете в оценке релевантности документов для нашего проекта FindMyShoes! Ниже представлено несколько запросов, а также топ-10 документов, выданных нашей системой по запросу. Мы просим вас поставить для каждого документа две оценки:', file=person_task)
        print(' - оценку релевантности - число от 1 до 5', file=person_task)
        print(' - оценку соответствия фильтрам - число от 0 до 1\n', file=person_task)
        print('Критерии оценки вы можете посмотреть [здесь](https://github.com/ItsLastDay/FindMyShoes/blob/master/docs/assessment/criteria.md).  ', file=person_task)
        print('Чтобы внести свои оценки в файл, сделайте pull request.', file=person_task)
        print('\n\n\n', file=person_task)
        
        for i in range(min(len(all_tasks), 5)):
            next_task = None
            while True:
                random.shuffle(all_tasks)
                if all_tasks[-1][0] not in tasks_for_this_person:
                    next_task = all_tasks[-1]
                    break
            all_tasks.pop(-1)
            tasks_for_this_person.add(next_task[0])

            print('### {}  '.format(next_task[0]), file=person_task)
            for doc in next_task[1]:
                print(doc + '  ', file=person_task)
                print('Оценка релевантности:   ', file=person_task)
                print('Оценка соответствия фильтрам:   ', file=person_task)
                print('  ', file=person_task)
            print('  \n  \n  \n', file=person_task)
