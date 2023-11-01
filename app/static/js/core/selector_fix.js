let searchParams = new URLSearchParams(window.location.search)

if (searchParams.has('bootcamp')) {
    const bootcampValue = searchParams.get('bootcamp')
    document.querySelector('#bootcamp').value = bootcampValue
}

if (searchParams.has('country')) {
    const countryValue = searchParams.get('country')
    document.querySelector('#country').value = countryValue
}

if (searchParams.has('state')) {
    const stateValue = searchParams.get('state')
    document.querySelector('#state').value = stateValue
}

if (searchParams.has('date')) {
    const dateValue = searchParams.get('date')
    document.querySelector('#date').value = dateValue
}

if (searchParams.has('experience')) {
    const experienceValue = searchParams.get('experience')
    document.querySelector('#experience').value = experienceValue
}


if (searchParams.has('metric')) {
    const metricValue = searchParams.get('metric')
    document.querySelector('#metric').value = metricValue
}