import ll
import os
import sys
import time


def main():
	print('src_id\tcategory\tset\tsubset\tnumber\tvariant\tname\tvalue\tcondition\tlanguage')

	rows = []

	# Non-Magic TCGs
	for i, row in enumerate(ll.csv('subcols/tcg_col.csv', dicts=False, stream=True)):
		if i==0:
			continue
		(cat_id, group_id, prod_id, subtype, game, set, number, name, vs, rarity, value, value_updated, lang) = row
		if 'Riftbound' in game:
			game = 'Riftbound'
		# print(ll.csv([prod_id, game, set, name, number, subtype, value, '', lang], delim='\t'))
		rows.append([prod_id, game, set, '', number, subtype, name, value, '', lang])

	# Sports and Star Wars
	hierarchy = ll.json('hierarchy_of_sports_sets.json')
	for i, row in enumerate(ll.csv('subcols/sports_col.csv', dicts=False, stream=True)):
		if i==0:
			continue
		(scp_id, sport, year, brand, set, name, number, parallel, price, condition) = row
		sport = ' '.join(map(ll.uppercamel, sport.split('-')))
		set = f'{year} {brand} {set}'.replace('&', 'and')
		if set in hierarchy[sport]:
			subset = ''
		else:
			main_set = max((k for k in hierarchy[sport] if set.startswith(k)), key=len)
			rest = ll.rempre(set, main_set).strip()
			set, subset = main_set, rest
		# print(ll.csv([scp_id, sport, set, name, number, parallel, price, condition, 'en'], delim='\t'))
		rows.append([scp_id, sport, set, subset, number, parallel, name, price, condition, 'en'])

	# Magic
	for i, row in enumerate(ll.csv('subcols/mtg.csv', dicts=False, stream=True)):
		if i==0:
			continue
		(_,_,name,sc,set,cn,foil,_,quant,_,sf_id,value,_,_,cond,lang,_) = row
		var = ll.uppercamel(foil) if (foil and foil != 'normal') else ''
		for _ in range(int(quant)):
			# print(ll.csv([sf_id, 'Magic', f'({sc}) {set}', name, cn, var, value, cond, lang], delim='\t'))
			rows.append([sf_id, 'Magic', f'{set}', '', cn, var, name, value, cond, lang])

	# Sort all rows
	# (or not)

	for row in rows:
		print(ll.csv(row, delim='\t'))

if __name__ == '__main__':
	main()
