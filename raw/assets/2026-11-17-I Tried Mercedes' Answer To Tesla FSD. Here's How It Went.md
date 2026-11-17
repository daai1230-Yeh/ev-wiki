---
title: "I Tried Mercedes' Answer To Tesla FSD. Here's How It Went"
author: Mack Hogan
date: 2026-11-16
source: https://insideevs.com/reviews/815471/mercedes-drive-assist-pro-review/
tags:
  - Mercedes-Benz
  - ADAS
  - Nvidia
  - Tesla-FSD
  - newsletter-clipping
  - InsideEVs
  - EV
clipped: 2026-11-17
---

# I Tried Mercedes' Answer To Tesla FSD. Here's How It Went

**Author**: Mack Hogan | **Date**: 2026-11-16

---

The point-to-point assistant can handle traffic lights, pedestrians, cyclists, and navigation duties. But it's not technically self-driving.

After years of having a market to itself, Tesla's Full Self-Driving (FSD) is about to have a real challenger. Mercedes is introducing MB.Drive Assist Pro, a similar point-to-point driver assistant that can maneuver the vehicle through crowded city streets, negotiating stoplights, pedestrian traffic, and construction zones along the way. Like with Tesla FSD, you're still legally driving, with attention required. But after sampling this technology in a 25-minute loop through downtown San Francisco, I came away impressed.

(Full disclosure: Mercedes flew me to San Francisco for the launch of MB.Drive Assist Pro. The company covered airfare, lodging, and meals, plus it provided test cars and demonstrations.)

## Who Can Get It?

MB.Drive Assist Pro will be available this spring in cars with the MB.OS operating system and required hardware. That means it's coming to the new CLA EV and hybrid, the GLC EV, the S-Class sedan, and the recently refreshed GLE and GLS SUVs. If you own one of those vehicles, you'll be able to purchase it in the Mercedes digital store on the vehicle, though pricing has not been announced. (GLC EV owners also need certain hardware that isn't standard, so it won't come to everyone.)

Beta testing is beginning shortly in California, so if you own one of those cars in the Golden State, keep an eye on your inbox. After the initial rollout next year, Mercedes plans to quickly deploy the tech to more gas, electric, and hybrid models.

Mercedes will also launch Hands-Free Highway Assist next year, enabling hands-off cruising on divided highways. But intra-city runs require hands on the wheel, at least nominally.

## Hands On The Wheel

There's one major distinction between MB.Drive Assist Pro and FSD: Drive Assist Pro requires a hand on the wheel in the city. Tesla will let you go hands-free anywhere, relying on a relatively easy-to-fool driver monitoring camera to keep you in the loop. (This does not always work.) Mercedes allows hands-free motoring with its highway-only Hands-Free Highway Assist, but if you're negotiating stop lights you'll need a hand on the tiller.

In theory, anyway. In reality the car often let me go five minutes or so without an intervention, as its nag reminders are contextual. If the driver monitoring camera sees that you're clearly paying attention and the car is in a relatively manageable situation, it's pretty laissez faire about your hands. Even when it does remind you, it doesn't take much to satisfy it.

## Under The Skin: It's Not End-To-End AI

MB.Drive Assist Pro is as much an Nvidia product as a Mercedes one. The system uses Nvidia's Drive AV stack for its fundamental approach to driving, with a system-on-chip that delivers up to 254 tera operations per second (TOPS). It uses that supercomputer to crunch the data from 10 cameras, five radars, and 12 ultrasonic sensors, giving it extra modalities beyond Tesla's camera-only approach. Mercedes says the radars should help with perception in heavy fog and at night.

But that's not the only way this system diverges from Tesla's approach. Tesla uses an end-to-end neural network, which means that data goes in, driving comes out, and everything in between is handled by varying the weights in the neural network. There are no deterministic, hard rules, rather just the collective "knowledge" of billions of miles of training data.

Mercedes and Nvidia are more risk averse than that. The system's fundamental driving character is handled by Nvidia's Alpamayo stack, which is a pure AI layer that navigates the uncertain and contextual driving world. But that system has a guardrail around it: a deterministic layer called Halos, with hard-coded, immutable rules. That means "stop at a stop sign" is not a highly weighted node in the system's black-box brain, it's a fact of life that the AI system works within.

Tesla used to use this sort of blended model, and I must say that FSD has improved rapidly in the years since it has become an end-to-end AI system. Still, as automakers feel out the safest way to do this, this is firmly the right way to start. Whether it can keep up with end-to-end AI systems is a different question, one we won't be able to answer for years.

## How Does It Drive?

My experience with Drive Assist Pro was brief. Mercedes gave us a 25-minute demo drive, during which I was "driving," albeit only in the legal sense. The car took us on an urban loop through San Francisco, starting in the dense Financial District and towards the Embarcadero.

Immediately, I was pleasantly surprised. Despite FSD's multi-year head start, the Mercedes system felt similarly confident to the FSD version I tested in late 2025. The car confidently and predictably navigated traffic from the beginning, with no obvious indecision or perception issues. I kept an eye on the car's perception the whole time through the built-in visualisation, which looked great and kept me feeling secure.

Still, the experience of a car making its own driving decisions is still unsettling on its own. Early on, the car was going left at an intersection with two left turn lanes. We were in the leftmost one and—anticipating a turn a few blocks ahead—the car started maneuvering into the second-to-left lane before the turn.

This was legal (to my knowledge), executed relatively safely, and properly signalled, but still a more risky maneuver than turning first before changing lanes. It confused both me and the car I was jumping ahead of, and made me nervous for a second.

That was really the only snag in the loop, though. I encountered double-parked cars, lights that turned red as I waited for a pedestrian to clear, and temporary construction zones. The Mercedes GLC EV test car handled them without drama. It seemed properly cautious, and the requirement to have a hand on the wheel definitely kept my focus sharp.

## Does It Feel Safe?

Here's the main thing I'm surprised by: I didn't expect Mercedes to pursue this path at all. Two years ago, my baseline assumption was that automakers would offer things like hands-free highway cruising for a while, but that a point-to-point system wouldn't launch on any legacy system before it was ready to be eyes-off level 4 autonomy.

A limited level 2 system like Super Cruise has obvious and clear delineations of responsibility and capability. Tesla FSD, meanwhile, is literally called "full self driving," and in my experience many buyers treat that as a fact, not a marketing slogan. When the car handles every aspect of driving, it's hard to remember that you are still legally in charge and responsible. I never expected a legacy automaker to open that can of worms.

Mercedes, ever afraid of being behind the curve, is making the leap. It has pulled its Drive Pilot level 3 eyes-off highway assistant from the market for the time being, betting big on the Nvidia-powered, hands-on Drive Assist Pro function.

Its approach certainly feels more cautious than Tesla's. In my brief experience, Drive Assist Pro felt far more refined than the first beta versions of Tesla FSD, and far more aware of the driver's attention. Through minutes of direct concentration I would never get nagged, but five seconds of daydreaming led to a warning.

It helps, too, that it's not labeled as "Self Driving," and that it is "collaborative." That means if you want to push the car wider around a cyclist, or cross the double yellow line to give parked cars some berth, you can do so without disabling the system. Grab the wheel and the car lets you steer however you'd like, seamlessly resuming control when you let go again. Ditto if you want the car to speed up; press the accelerator and you zoom ahead. Plus, if you want to break the speed limit, the system will let you set whatever speed you like, and climb to it if conditions permit. You're driving. It doesn't want you to forget that.

Those little choices made me feel safe. I felt like the expectations were clear, and that I could settle into the supervisory role I was assigned.

Will it work for normal buyers? That's a trickier question. Like FSD, Drive Assist Pro is so good that I could see it lulling less educated customers into false security. Mercedes seems intent on avoiding that, with a plan to question owners directly throughout the beta period. We'll have to wait to see if the company can explain it to customers, get it to market, and drive subscriptions. But as a first impression, I'd say Drive Assist Pro is a great start.

---

*Source: [InsideEVs](https://insideevs.com/reviews/815471/mercedes-drive-assist-pro-review/)*
