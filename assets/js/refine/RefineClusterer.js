import React from 'react'
import PropTypes from 'prop-types'
import { clusterByKey, clusterByKnn } from 'clustring'
import FormGroup from 'reactstrap/lib/FormGroup'
import Input from 'reactstrap/lib/Input'
import Label from 'reactstrap/lib/Label'
import fingerprint from 'clustring/key/fingerprint'
import levenshtein from 'clustring/knn/levenshtein'

const Algorithms = [
  {
    name: 'fingerprint',
    selectName: 'Fingerprint',
    description: 'Group values by fingerprint. This method is effective when values are capitalized irregularly or if special characters are used in some and not others. For instance, "café" and "Cafe" both have the same fingerprint, "cafe".',
    defaultOptions: null,
    optionFields: null,
    buildClusterer: (bucket) => clusterByKey(bucket, fingerprint())
  },
  {
    name: 'levenshtein',
    selectName: 'Edit distance',
    description: 'Groups values if the number of characters added, edited or deleted to get from one value to the other is equal or inferior to \'Maximum distance\'. For instance, the distance between "Cafés" and "cafe" is 3.',
    defaultOptions: { maxDistance: 3 },
    optionFields: (handlers, options) => (
      <FormGroup>
        <Label for="refine-clusterer-max-distance">Maximum distance</Label>
        <Input id="refine-clusterer-max-distance" type="number" required name="maxDistance" size="2" value={options.maxDistance} min="1" max="999" placeholder="3" {...handlers} />
      </FormGroup>
    ),
    buildClusterer: (bucket, options) => clusterByKnn(bucket, levenshtein(options.maxDistance), options.maxDistance)
  }
]

export default class RefineClusterer extends React.PureComponent {
  static propTypes = {
    bucket: PropTypes.object.isRequired, // { "str": Number(count), ... }
    onProgress: PropTypes.func.isRequired, // onProgress(0.2) => undefined (means 20% clustered)
    onComplete: PropTypes.func.isRequired, // onComplete(bins) => undefined (bins is [ { name, count, bucket }, ... ])
  }

  state = {
    clusterer: this._startClusterer(Algorithms[0], Algorithms[0].defaultOptions),
    algorithm: Algorithms[0],
    clustererOptions: Algorithms[0].defaultOptions
  }

  _startClusterer (algorithm, options) {
    const clusterer = algorithm.buildClusterer(this.props.bucket, options)

    const reportProgressUntilDoneOrCanceled = () => {
      if (clusterer.canceled) return
      if (clusterer.progress >= 1) return

      this.props.onProgress(clusterer.progress)
      setTimeout(reportProgressUntilDoneOrCanceled, 20)
    }
    reportProgressUntilDoneOrCanceled()

    clusterer.cluster()
      .then(bins => {
        if (clusterer.canceled) {
          // the only way clusterer is canceled is if another is running --
          // meaning we don't want to hear from this one. Ignore the result.
          return
        }
        this.props.onComplete(bins)
      })
      .catch(err => {
        // only error is "canceled". Ignore it.
      })
    return clusterer // so it can be canceled
  }

  componentWillUnmount () {
    this.state.clusterer.cancel() // it'll die asynchronously
  }

  /**
   * Kick off a new clusterer.
   */
  setClusterer (algorithm, clustererOptions) {
    // 1. Start a state transition, which is async.
    // (https://reactjs.org/docs/faq-state.html#when-is-setstate-asynchronous)
    this.setState(prevState => {
      if (prevState.clusterer !== null) {
        prevState.clusterer.cancel()
      }

      const clusterer = this._startClusterer(algorithm, clustererOptions)

      return {
        clusterer,
        algorithm,
        clustererOptions: clustererOptions
      }
    })
  }

  selectClusterer = (ev) => {
    const name = ev.target.value
    const algorithm = Algorithms.find(a => a.name === name)
    this.setClusterer(algorithm, algorithm.defaultOptions || null)
  }

  onChangeOption = (ev) => {
    const { algorithm } = this.state

    const el = ev.target
    const name = el.name
    let value = el.value
    if (el.type === 'number') value = Number(value)

    const clustererOptions = {
      ...this.state.clustererOptions,
      [name]: value
    }

    this.setClusterer(algorithm, clustererOptions)
  }

  renderSelect = () => {
    const { algorithm } = this.state
    const options = Algorithms.map(({ name, selectName }) => <option key={name} value={name}>{selectName}</option>)

    return (
      <select name='algorithm' className='custom-select' value={algorithm.name} onChange={this.selectClusterer}>
        {options}
      </select>
    )
  }

  renderOptions () {
    const { algorithm, clustererOptions } = this.state
    if (!algorithm.optionFields) return null

    const handlers = {
      onChange: this.onChangeOption,
    }

    return (
      <div className="method-options form-inline">
        {algorithm.optionFields(handlers, clustererOptions)}
      </div>
    )
  }

  render () {
    const { algorithm } = this.state

    return (
      <div className="refine-clusterer">
        <legend>Method</legend>
        <div className="method">
          <div className="method-select">
            {this.renderSelect()}
          </div>
          <div className="method-form">
            <div className="method-description">
              {algorithm.description}
            </div>
            {this.renderOptions()}
          </div>
        </div>
      </div>
    )
  }
}
