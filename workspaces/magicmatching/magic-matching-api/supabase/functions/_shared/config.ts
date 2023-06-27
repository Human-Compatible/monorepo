class Config {
	constructor() {
		// ...
		// determine dev vs prod mode
		this.mode = 'localdev';
	}

	mode = 'production';

	site_name = 'Magic Matching';

	gql_uri = 'https://localdev.cngarrison.com:8043/graphql'; 

	openai_key = '';

	setMode(mode) {
		this.mode = mode;
		// change all the other things that depend on this... or maybe we can't since everything is frozen
	}
}

const configInstance = new Config();

Object.freeze(configInstance);

export default configInstance;
