import ll
import os
import sys
import time


def main():
	def _inner(f):
		f.write('src_id\tcategory\tset\tsubset\tnumber\tvariant\tname\tvalue\tcondition\tlanguage\tpsa_10\tcgc_10\tgrade_9' + '\n')

		rows = []

		# pbar = ll.pbar(title='Processing: ', total=total)

		# Non-Magic TCGs
		for i, row in enumerate(ll.csv('subcols/tcg_col.csv', dicts=False, stream=True)):
			if i==0:
				continue
			(cat_id, group_id, prod_id, subtype, game, set, number, name, vs, rarity, value, value_updated, lang, condition, psa_10, cgc_10, psa_9) = row
			if 'Riftbound' in game:
				game = 'Riftbound'
			# print(ll.csv([prod_id, game, set, name, number, subtype, value, '', lang], delim='\t'))
			rows.append([prod_id, game, set, '', number, subtype, name, value, condition, lang, psa_10, cgc_10, psa_9])

			yield

		# Sports and Star Wars
		hierarchy = ll.json('hierarchy_of_sports_sets.json')
		for i, row in enumerate(ll.csv('subcols/sports_col.csv', dicts=False, stream=True)):
			if i==0:
				continue
			(scp_id, sport, year, brand, set, name, number, parallel, price, condition, psa_10, cgc_10, psa_9) = row
			sport = ' '.join(map(ll.uppercamel, sport.split('-')))
			set = f'{year} {brand} {set}'.replace('&', 'and')
			if set in hierarchy[sport]:
				subset = ''
			else:
				main_set = max((k for k in hierarchy[sport] if set.startswith(k)), key=len)
				rest = ll.rempre(set, main_set).strip()
				set, subset = main_set, rest
			# print(ll.csv([scp_id, sport, set, name, number, parallel, price, condition, 'en'], delim='\t'))
			rows.append([scp_id, sport, set, subset, number, parallel, name, price, condition, 'en', psa_10, cgc_10, psa_9])

			yield

		# Magic

		# Index cards to search for their flavor names in the JSON
		sccn2row = {}
		for i, row in enumerate(ll.csv('subcols/mtg.csv', dicts=False, stream=True)):
			if i==0:
				continue
			(_,_,name,sc,set,cn,foil,_,quant,_,sf_id,value,_,_,cond,lang,_) = row
			sccn = f"{sc}\t{cn}"
			sccn2row[sccn] = row

			yield

		# Load flavor names from the JSON
		sccn2fname = {}
		for line in ll.lines('scryfall.json', stream=True):
			if not line.startswith('{'):
				continue
			if line.endswith(','):
				line = line[:-1]
			j = ll.json(line)
			sccn = f"{j['set']}\t{j['collector_number']}"
			if sccn in sccn2row:
				if (fname:=j.get('flavor_name')):
					sccn2fname[sccn] = fname

			yield

		# Actually process the collection file now
		for i, row in enumerate(ll.csv('subcols/mtg.csv', dicts=False, stream=True)):
			if i==0:
				continue
			(_,_,name,sc,set,cn,foil,_,quant,_,sf_id,value,_,_,cond,lang,_) = row
			sccn = f"{sc}\t{cn}\t{name}"
			sccn2row[sccn] = row
			var = ll.uppercamel(foil.strip()) if (foil.strip() and foil.strip() != 'normal') else ''
			for _ in range(int(quant)):
				# print(ll.csv([sf_id, 'Magic', f'({sc}) {set}', name, cn, var, value, cond, lang], delim='\t'))
				rows.append([sf_id, 'Magic', f'{set}', '', cn, var, name, value, cond, lang, '', '', ''])

			yield
			# TODO: resolve w/ tcg lib, for many reasons, including to get graded prices
			# import tcg
			# print(tcg.mtg.card(set, cn).realize(variant=var or 'normal').graded_price('manual-only-price'))

		# Sort all rows
		# (or not)

		for row in rows:
			for i, v in enumerate(row):
				if not isinstance(v, str) and float(v)==0:
					row[i] = ''
				elif isinstance(v, str):
					v = v.strip()
					try:
						if v and float(v) == 0.00:
							row[i] = ''
					except:
						if v.isnumeric() and int(v) == 0:
							row[i] = ''

			if row[-4] == 'ja':
				row[-4] = 'jp'
			elif row[-4] == '':
				row[-4] = 'en'
			if row[-6] == 0:
				row[-6] = ''
			row[-8] = ' '.join(ll.capitalize(w) for w in row[-8].split())
			f.write(ll.csv(row, delim='\t') + '\n')

	# Establish an overall total for the progress bar
	total = 0
	total += ll.wc_l('subcols/tcg_col.csv') - 1
	total += ll.wc_l('subcols/sports_col.csv') - 1
	total += ll.wc_l('subcols/mtg.csv') - 1
	total += ll.wc_l('scryfall.json') - 2
	total += ll.wc_l('subcols/mtg.csv') - 1 # [sic]

	with open('collection.csv', 'w+') as f:
		# Do it.
		for _ in ll.track(_inner(f), total=total):
			pass


if __name__ == '__main__':
	main()
