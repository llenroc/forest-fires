import sys
import pickle
import time
import datetime
import keras
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from scoring import return_scores
from data_manip.tt_splits import tt_split_all_less60
from sklearn.grid_search import GridSearchCV
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD, RMSprop
from keras.utils import np_utils


def get_model(model_name, train_data): 
	'''
	Input: String, Pandas DataFrame
	Output: Instantiated Model
	'''
	random_seed=24
	if model_name == 'logit': 
		return LogisticRegression(random_state=random_seed)
	elif model_name == 'random_forest': 
		return RandomForestClassifier(random_state=random_seed)
	elif model_name == 'gradient_boosting': 
		return GradientBoostingClassifier(random_state=random_seed)
	elif model_name == 'neural_net': 
		return get_neural_net(train_data)

def fit_model(train_data, model_to_fit):
	'''
	Input: Pandas DataFrame, Instantiated Model
	Output: Fitted model

	Using the fire column as the target and the remaining columns as the features, fit 
	the inputted model. 
	'''

	target, features = get_target_features(train_data)

	model_to_fit.fit(features, target)
	return model_to_fit

def predict_with_model(test_data, model): 
	'''
	Input: Pandas DataFrame, Fitted Model
	Output: Numpy Array of Predictions

	Using the fitted model, make predictions with the test data and return those predictions. 
	'''

	target, features = get_target_features(test_data)
	if isinstance(model, keras.models.Sequential): 
		predictions, predicted_probs = model.predict(features.values)[:, 1] > 0.50, model.predict_proba(features.values)
	else: 
		predictions, predicted_probs = model.predict(features), model.predict_proba(features)

	return predictions, predicted_probs

def log_results(model_name, train, fitted_model, scores): 
	'''
	Input: String, Pandas DataFrame,  Dictionary
	Output: .txt file. 

	Log the results of this run to a .txt file, saving the column names (so I know what features I used), 
	the model name (so I know what model I ran), the parameters for that model, 
	and the scores associated with it (so I know how well it did). 
	'''

	st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	filename = './modeling/logs/' + model_name + '.txt'
	with open(filename, 'a+') as f:
		f.write(st + '\n')
		f.write('-' * 100 + '\n')
		f.write('Model Run: ' + model_name + '\n' * 2)
		f.write('Params: ' + str(fitted_model.get_params()) + '\n' * 2)
		f.write('Features: ' + ', '.join(train.columns) + '\n' * 2)
		f.write('Scores: ' + str(scores) + '\n' * 2)

def grid_search(model_name, train_data, test_data): 
	'''
	Input: String
	Output: Best fit model from grid search parameters. 

	For the given model name, grab a model and the relevant grid parameters, perform a grid search 
	with those grid parameters, and return the best model. 
	'''

	model = get_model(model_name, train_data)
	if isinstance(model, keras.models.Sequential): 
		train_target, train_features = get_target_features(train_data)
		test_target, test_features = get_target_features(test_data)
		train_target, test_target = np_utils.to_categorical(train_target, 2), np_utils.to_categorical(test_target, 2) 
		train_features, test_features = train_features.values, test_features.values
		model.fit(train_features, train_target, batch_size=150, nb_epoch=20, validation_data=(test_features, test_target))
		return model
	grid_parameters = get_grid_params(model_name)
	grid_search = GridSearchCV(estimator=model, param_grid=grid_parameters, scoring='roc_auc')
	target, features = get_target_features(train_data)
	grid_search.fit(features, target)

	return grid_search.best_estimator_

def get_neural_net(train_data): 
	'''
	Input: Integer, Pandas DataFrame
	Output: Instantiated Neural Network model

	Instantiate the neural net model and output it to train with. 
	'''
	hlayer_1_nodes = 200
	hlayer_2_nodes = 200
	model = Sequential()

	model.add(Dense(train_data.shape[1] - 1, hlayer_1_nodes, init='uniform'))
	model.add(Activation('relu'))
	model.add(Dropout(0.35))
	model.add(Dense(hlayer_1_nodes, hlayer_2_nodes, init='uniform'))
	model.add(Activation('relu'))
	model.add(Dropout(0.35))
	model.add(Dense(hlayer_2_nodes, 2, init='uniform'))
	model.add(Activation('softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='adadelta')

	return model

def get_grid_params(model_name): 
	'''
	Input: String
	Output: Dictionary
	'''
	if model_name == 'logit': 
		return {'penalty': ['l2', 'l1'], 'C': [0.1, 0.5, 1, 2, 10]}
	elif model_name == 'random_forest': 
		return {'n_estimators': [500], 
				'max_depth': [3, 5, 10, 20]}
	elif model_name == 'gradient_boosting': 
		return {'learning_rate': [0.01, 0.05, 0.1]}

def get_target_features(df): 
	'''
	Input: Pandas DataFrame
	Output: Numpy Array, Numpy Array	

	For the given dataframe, grab the target and features (fire bool versus all else) and return them. 
	'''

	target = df.fire_bool
	features = df.drop('fire_bool', axis=1)
	return target, features


if __name__ == '__main__': 
	# sys.argv[1] will hold the name of the model we want to run (logit, random forest, etc.), 
	# and sys.argv[2] will hold our input dataframe (data will all the features and target). 
	model_name = sys.argv[1]

	with open(sys.argv[2]) as f: 
		input_df = pickle.load(f)
	
	train, test = tt_split_all_less60(input_df)

	'''
	keep_list = ['conf']
	train = train[keep_list]
	test = test[keep_list]
	train = train.drop(keep_list, axis=1)
	test = test.drop(keep_list, axis=1)
	'''
	
	fitted_model = grid_search(model_name, train, test)
	preds, preds_probs = predict_with_model(test, fitted_model)
	scores = return_scores(test.fire_bool, preds, preds_probs)
	log_results(model_name, train, fitted_model, scores)



